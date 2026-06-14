import chompjs
import pandas as pd
import requests

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


def get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata) -> IngatlanDataFrame:
    id_to_name = {obj["id"]: obj["nev"] for obj in ksh_metadata}
    id_to_tipus = {obj["id"]: obj["tipus"] for obj in ksh_metadata}

    df = pd.DataFrame(ksh_raw_data)
    df["megye_nev"] = df["megye"].map(id_to_name)
    df["telepules_nev"] = df["telaz"].map(id_to_name)
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

    df = df.sort_values(by=["datum", "szint", "megye", "telaz"])
    df = df.reset_index(drop=True)

    df = KshIngatlanAdatSchema.validate(df)

    return df
