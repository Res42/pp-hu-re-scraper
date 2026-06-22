import io
from datetime import datetime

import polars as pl
import polars.selectors as cs
import requests

from models.mnb import MnbDataFrame, MnbLakasarindexSchema, m


def download_mnb_lakasarindex() -> bytes:
    current_year = datetime.now().year
    base_url = "https://statisztika.mnb.hu/timeseries/MNB_lakasarindex_{}Q{}.xlsx"

    for target_year in range(current_year, current_year - 2, -1):
        for q in [4, 3, 2, 1]:
            url = base_url.format(target_year, q)
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    return response.content
            except requests.RequestException:
                continue

    raise RuntimeError(
        "Nem sikerült letölteni az MNB lakásárindex fájlt egyetlen negyedévre sem!"
    )


def get_mnb_lakasarindex(
    mnb_lakasarindex: bytes,
) -> MnbDataFrame:
    df = pl.read_excel(
        source=io.BytesIO(mnb_lakasarindex),
        sheet_name="1.1",
        read_options={
            "header_row": 3,
        },
    )

    df = df.head(-2)

    new_names = [
        "quarter",
        m.aggregated,
        m.budapest,
        m.varosok,
        m.varosok_del_alfold,
        m.varosok_del_dunantul,
        m.varosok_eszak_alfold,
        m.varosok_eszak_magyarorszag,
        m.varosok_kozep_dunantul,
        m.varosok_pest,
        m.varosok_nyugat_dunantul,
        m.kozsegek,
    ]

    df = df.select(df.columns).rename(dict(zip(df.columns, new_names)))

    df = df.with_columns(
        [
            pl.col("quarter").str.extract(r"(\d{4})").forward_fill().alias("_ev"),
            pl.col("quarter").str.extract(r"([I|V|X]+)\.").alias("_romai"),
        ]
    )

    roman_quarter_map = {"I": "-03-31", "II": "-06-30", "III": "-09-30", "IV": "-12-31"}

    df = df.with_columns(
        pl.concat_str(
            [
                pl.col("_ev"),
                pl.col("_romai").replace_strict(roman_quarter_map, default=None),
            ]
        )
        .str.to_date("%Y-%m-%d")
        .alias(m.datum)
    ).drop(["_ev", "_romai", "quarter"])

    df = df.with_columns(cs.all().exclude("datum").cast(pl.Float64, strict=False))

    df = df.sort(m.datum)

    df = MnbLakasarindexSchema.validate(df)
    df = pl.DataFrame(df)

    return df
