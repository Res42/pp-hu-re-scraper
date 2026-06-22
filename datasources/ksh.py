import chompjs
import polars as pl
import requests
from slugify import slugify

from models.ksh import (
    KSH_RAW_INPUT_SCHEMA,
    MEGYE_FILTER,
    TELEPULES_FILTER,
    IngatlanTipus,
    KshIngatlanAdatSchema,
    c,
    cr,
)

KSH_INGATLAN_ADATTAR_JSON_URL = "https://www.ksh.hu/s/ingatlanadattar/inga-data.json"
KSH_INGATLAN_ADATTAR_METADATA_JSON_URL = (
    "https://www.ksh.hu/s/ingatlanadattar/assets/teleplist.js"
)

# fmt: off
KOZTER_CLEANING_DF = pl.DataFrame({
    "telaz":   ["18069",       "14216",                "02112",                    "18616",               "25584"             ],
    "kozter":  ["Kőrös utca",  "Gombócz Zoltán utca",  "Rákosmezei repülők útja",  "Gerecz Attila utca",  "Bólyai Farkas utca"],
    "helyes":  ["Körös utca",  "Gombocz Zoltán utca",  "Rákosmezei Repülők útja",  "Gérecz Attila utca",  "Bolyai Farkas utca"],
})
# fmt: on


def download_ksh_ingatlan_adattar():
    response = requests.get(KSH_INGATLAN_ADATTAR_JSON_URL, timeout=15)
    response.raise_for_status()

    return response.json()


def download_ksh_ingatlan_adattar_metadata():
    response = requests.get(KSH_INGATLAN_ADATTAR_METADATA_JSON_URL, timeout=15)
    response.raise_for_status()

    raw = response.text

    return chompjs.parse_js_object(raw)


def _ensure_no_uncleaned_data(df: pl.DataFrame, id_to_name: dict):
    """
    Jelenleg a kód feltételezi, hogy egy településen belül nincs olyan két különböző közterület,
    amiknek egyező slugify(<közterület>)-e van.
    """

    check_df = df.select([cr.telaz, cr.kozter, c.output_path, c.datum]).unique()

    collisions = (
        check_df.with_columns(
            pl.len().over([c.output_path, c.datum]).alias("row_count")
        )
        .filter(pl.col("row_count") > 1)
        .drop("row_count")
    )

    if not collisions.is_empty():
        error_details = []

        for (output_path,), group in collisions.group_by([c.output_path]):
            telaz = group[c.telaz].to_list()[0]
            telepules_nev = id_to_name.get(telaz, f"Ismeretlen ID: {telaz}")

            raw_names = group[cr.kozter].unique().to_list()

            error_details.append(
                f"  - KSH [{telepules_nev} (telaz: {telaz})] -> Fájl: '{output_path}' | Ütköző eredeti nevek: {raw_names}"
            )

        raise AssertionError(
            "HIBA: A slugify névütközést okozott!\n"
            + "\n".join(error_details)
            + "\n\nFejlesztői beavatkozás szükséges! "
            + "El kell dönteni, hogy ez hibás adat (ilyenkor fel kell venni a cleaner.py-be) "
            + "vagy tényleg létezik ez a két közterület (fejlesztés szükséges, hogy a slugify meg tudja különböztetni őket)."
        )


def get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata) -> pl.DataFrame:
    id_to_name = {obj["id"]: obj["nev"] for obj in ksh_metadata}
    id_to_tipus = {obj["id"]: obj["tipus"] for obj in ksh_metadata}

    df = pl.DataFrame(ksh_raw_data, schema=KSH_RAW_INPUT_SCHEMA)

    # Egyes közterületek rosszul / duplikáltan / több néven vannak felvéve a KSH adatokban,
    # ezeket át kell alakítani a helyes nevükre, hogy késcőbb helyesen legyenek csoportosítva.
    df = (
        df.join(KOZTER_CLEANING_DF, on=[cr.telaz, cr.kozter], how="left")
        .with_columns(pl.col("helyes").fill_null(pl.col(cr.kozter)).alias(cr.kozter))
        .drop("helyes")
    )

    df = df.with_columns(
        [
            pl.col(cr.megye)
            .replace(id_to_name)
            .map_elements(slugify, pl.String)
            .alias("megye_slug"),
            pl.col(cr.telaz)
            .replace(id_to_name)
            .map_elements(slugify, pl.String)
            .alias("telepules_slug"),
            pl.col(cr.kozter)
            .map_elements(slugify, pl.String, skip_nulls=True)
            .alias("kozter_slug"),
            pl.col(cr.telaz)
            .replace(id_to_tipus)
            .cast(pl.Int64)
            .alias(c.telepules_tipus),
            pl.col(cr.cshaz_ar) * 1000,
            pl.col(cr.tobbl_ar) * 1000,
            pl.col(cr.panel_ar) * 1000,
            pl.col(cr.total_ar) * 1000,
            pl.date(pl.col(cr.ev), 12, 31).alias(c.datum),
        ]
    )

    price_cols = IngatlanTipus.price_cols()
    col_to_filename = IngatlanTipus.col_file_name_dict()
    col_to_type_str = IngatlanTipus.col_to_type_dict()

    index_cols = [col for col in df.columns if col not in price_cols]

    df = df.unpivot(
        on=price_cols,
        index=index_cols,
        variable_name=c.ingatlan_tipus,
        value_name=c.ar,
    ).drop_nulls(subset=[c.ar])

    df = df.with_columns(
        [
            pl.col(c.ingatlan_tipus).replace(col_to_type_str).alias(c.ingatlan_tipus),
            pl.col(c.ingatlan_tipus).replace(col_to_filename).alias("target_filename"),
            pl.col(c.ar).cast(pl.Int64),
        ]
    )

    df = df.with_columns(
        pl.when(MEGYE_FILTER)
        .then(pl.concat_str(["megye_slug", "target_filename"], separator="/"))
        .when(TELEPULES_FILTER)
        .then(
            pl.concat_str(
                ["megye_slug", "telepules_slug", "target_filename"], separator="/"
            )
        )
        .otherwise(
            pl.concat_str(
                ["megye_slug", "telepules_slug", "kozter_slug", "target_filename"],
                separator="/",
            )
        )
        .alias(c.output_path)
    )

    _ensure_no_uncleaned_data(df, id_to_name)

    df = df.drop(
        [
            "target_filename",
            "megye_slug",
            "telepules_slug",
            "kozter_slug",
            "szoras",
            "idosor",
            "cshaz_db",
            "tobbl_db",
            "panel_db",
            "total_db",
        ]
    )

    df = df.sort([c.datum, c.output_path])

    df = KshIngatlanAdatSchema.validate(df)

    return df
