import io
from datetime import datetime

import pandas as pd
import requests

from models.mnb import MnbDataFrame, MnbLakasarindexSchema


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
    df = pd.read_excel(
        io.BytesIO(mnb_lakasarindex),
        sheet_name="1.1",
        decimal=",",
        skiprows=4,
        header=None,
        skipfooter=3,
    )

    # az első oszlop üres, azt töröljük
    df = df.iloc[:, 1:]
    df.columns = [
        "quarter",
        "aggregated",
        "budapest",
        "varosok",
        "varosok_del_alfold",
        "varosok_del_dunantul",
        "varosok_eszak_alfold",
        "varosok_eszak_magyarorszag",
        "varosok_kozep_dunantul",
        "varosok_pest",
        "varosok_nyugat_dunantul",
        "kozsegek",
    ]

    # római negyedév átalakítása
    parsed_quarters = df["quarter"].str.extract(r"(?:(\d{4})\.\s*)?([I|V|X]+)\.")
    parsed_quarters.columns = ["ev", "romai"]
    parsed_quarters["ev"] = parsed_quarters["ev"].ffill()
    df["ev"] = parsed_quarters["ev"]
    df["romai"] = parsed_quarters["romai"]
    roman_quarter_map = {"I": "-03-31", "II": "-06-30", "III": "-09-30", "IV": "-12-31"}

    def build_date(row):
        suffix = roman_quarter_map.get(row["romai"])
        return pd.to_datetime(row["ev"] + suffix)

    df.insert(1, "datum", df.apply(build_date, axis=1))
    df = df.drop(columns=["ev", "romai"])

    # számok helyrerakása
    for col in [
        "aggregated",
        "budapest",
        "varosok",
        "varosok_del_alfold",
        "varosok_del_dunantul",
        "varosok_eszak_alfold",
        "varosok_eszak_magyarorszag",
        "varosok_kozep_dunantul",
        "varosok_pest",
        "varosok_nyugat_dunantul",
        "kozsegek",
    ]:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].str.replace(",", ".")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("datum")
    df = df.reset_index(drop=True)

    df = MnbLakasarindexSchema.validate(df)

    return df
