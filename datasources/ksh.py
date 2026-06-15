import chompjs
import pandas as pd
import requests
from slugify import slugify

from datasources.cleaner import KOZTER_CLEANING_MAP
from models.ksh import IngatlanDataFrame, KshIngatlanAdatSchema

KSH_INGATLAN_ADATTAR_JSON_URL = "https://www.ksh.hu/s/ingatlanadattar/inga-data.json"
KSH_INGATLAN_ADATTAR_METADATA_JSON_URL = (
    "https://www.ksh.hu/s/ingatlanadattar/assets/teleplist.js"
)


def download_ksh_ingatlan_adattar():
    response = requests.get(KSH_INGATLAN_ADATTAR_JSON_URL, timeout=15)
    response.raise_for_status()

    return response.json()


def download_ksh_ingatlan_adattar_metadata():
    response = requests.get(KSH_INGATLAN_ADATTAR_METADATA_JSON_URL, timeout=15)
    response.raise_for_status()

    raw = response.text

    return chompjs.parse_js_object(raw)


def _ensure_no_uncleaned_data(df: pd.DataFrame, id_to_name: dict):
    """
    Jelenleg a kód feltételezi, hogy egy településen belül nincs olyan két különböző közterület,
    amiknek egyező slugify(<közterület>)-e van.
    """

    unique_pairs = df[["telaz", "kozter", "kozter_slug"]].drop_duplicates().dropna()

    # 2. Innen a kódod teljesen változatlanul és biztonságosan fut tovább:
    collision_mask = unique_pairs.duplicated(
        subset=["telaz", "kozter_slug"], keep=False
    )

    if collision_mask.any():
        collisions = unique_pairs[collision_mask]
        error_details = []
        for (telaz, slug), group in collisions.groupby(["telaz", "kozter_slug"]):
            telepules_nev = id_to_name[telaz]
            raw_names = group["kozter"].tolist()
            error_details.append(
                f"  - KSH [{telepules_nev}] -> Slug: '{slug}' | Ütköző eredeti nevek: {raw_names}"
            )

        raise AssertionError(
            "HIBA: A slugify névütközést okozott!\n"
            + "\n".join(error_details)
            + "\n\nFejlesztői beavatkozás szükséges! "
            + "El kell dönteni, hogy ez hibás adat (ilyenkor fel kell venni a cleaner.py-be) "
            + "vagy tényleg létezik ez a két közterület (fejlesztés szükséges, hogy a slugify meg tudja különböztetni őket)."
        )


def get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata) -> IngatlanDataFrame:
    id_to_name = {obj["id"]: obj["nev"] for obj in ksh_metadata}
    id_to_tipus = {obj["id"]: obj["tipus"] for obj in ksh_metadata}

    df = pd.DataFrame(ksh_raw_data)
    df["megye_slug"] = df["megye"].map(id_to_name).map(slugify)
    df["telepules_slug"] = df["telaz"].map(id_to_name).map(slugify)
    df["kozter_slug"] = df["kozter"].map(slugify, na_action="ignore")
    df["tipus"] = df["telaz"].map(id_to_tipus)
    df["cshaz_ar"] = df["cshaz_ar"] * 1000
    df["tobbl_ar"] = df["tobbl_ar"] * 1000
    df["panel_ar"] = df["panel_ar"] * 1000
    df["total_ar"] = df["total_ar"] * 1000
    df["datum"] = df["ev"].astype(str) + "-12-31"
    df = df.drop(
        columns=[
            "ev",
            "szoras",
            "idosor",
            "cshaz_db",
            "tobbl_db",
            "panel_db",
            "total_db",
        ]
    )

    # Egyes közterületek rosszul / duplikáltan / több néven vannak felvéve a KSH adatokban,
    # ezeket át kell alakítani a helyes nevükre, hogy később helyesen legyenek csoportosítva.
    for telaz, kozter_map in KOZTER_CLEANING_MAP.items():
        telaz_mask = df["telaz"] == telaz
        df.loc[telaz_mask, "kozter"] = df.loc[telaz_mask, "kozter"].replace(kozter_map)

    df = df.sort_values(by=["datum", "szint", "megye", "telaz"])
    df = df.reset_index(drop=True)

    _ensure_no_uncleaned_data(df, id_to_name)

    df = KshIngatlanAdatSchema.validate(df)

    return df
