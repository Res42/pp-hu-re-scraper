import pandas as pd

from models.ksh import IngatlanDataFrame, TelepulesTipus, c
from models.mnb import MnbDataFrame, m

_MEGYE_REGIO_MAP = {
    "13": m.varosok_pest,  # Pest
    "07": m.varosok_kozep_dunantul,  # Fejér
    "11": m.varosok_kozep_dunantul,  # Komárom-Esztergom
    "19": m.varosok_kozep_dunantul,  # Veszprém
    "08": m.varosok_nyugat_dunantul,  # Győr-Moson-Sopron
    "18": m.varosok_nyugat_dunantul,  # Vas
    "20": m.varosok_nyugat_dunantul,  # Zala
    "02": m.varosok_del_dunantul,  # Baranya
    "14": m.varosok_del_dunantul,  # Somogy
    "17": m.varosok_del_dunantul,  # Tolna
    "05": m.varosok_eszak_magyarorszag,  # Borsod-Abaúj-Zemplén
    "10": m.varosok_eszak_magyarorszag,  # Heves
    "12": m.varosok_eszak_magyarorszag,  # Nógrád
    "09": m.varosok_eszak_alfold,  # Hajdú-Bihar
    "15": m.varosok_eszak_alfold,  # Szabolcs-Szatmár-Bereg
    "16": m.varosok_eszak_alfold,  # Jász-Nagykun-Szolnok
    "03": m.varosok_del_alfold,  # Bács-Kiskun
    "04": m.varosok_del_alfold,  # Békés
    "06": m.varosok_del_alfold,  # Csongrád-Csanád
}


def _get_mnb_column_for_ksh_row(megye_kod: str, tipus: TelepulesTipus) -> str:
    if (
        tipus in [TelepulesTipus.BUDAPEST, TelepulesTipus.BUDAPEST_KERULET]
        or megye_kod == "01"
    ):
        return m.budapest

    if tipus == TelepulesTipus.KOZSEG:
        return m.kozsegek

    if megye_kod in _MEGYE_REGIO_MAP:
        return _MEGYE_REGIO_MAP[megye_kod]

    return m.varosok


def add_mnb_to_ksh(
    df_ksh: IngatlanDataFrame, df_mnb: MnbDataFrame
) -> IngatlanDataFrame:
    """
    Negyedévesíti a KSH DataFrame-et: minden KSH év közé beszúrja a negyedéves MNB pontokat (Q1, Q2, Q3),
    és kiszámolja rájuk a piaci indexarányos negyedéves árakat.
    """
    if df_ksh.empty:
        return df_ksh

    df_mnb_filtered = df_mnb[(df_mnb[m.datum] >= df_ksh[c.datum].min())].sort_values(
        m.datum
    )

    if df_mnb_filtered.empty:
        return df_ksh

    mnb_col = _get_mnb_column_for_ksh_row(
        str(df_ksh[c.megye].iloc), df_ksh[c.tipus].iloc
    )

    df_mnb_skeleton = pd.DataFrame(
        {c.datum: df_mnb_filtered[c.datum], "mnb_index": df_mnb_filtered[mnb_col]}
    )

    df_merged = pd.merge(df_mnb_skeleton, df_ksh, on=c.datum, how="left")

    meta_cols = [
        c.szint,
        c.tipus,
        c.megye,
        c.megye_slug,
        c.telaz,
        c.telepules_slug,
        c.kozter,
        c.kozter_slug,
    ]
    df_merged[meta_cols] = df_merged[meta_cols].ffill().bfill()

    for price_col in [c.tobbl_ar, c.total_ar, c.cshaz_ar, c.panel_ar]:
        if price_col in df_merged.columns and df_merged[price_col].notna().any():
            ratio_col = f"{price_col}_ratio"
            df_merged[ratio_col] = df_merged[price_col].astype(float) / df_merged[
                "mnb_index"
            ].astype(float)

            df_merged[ratio_col] = df_merged[ratio_col].interpolate(
                method="linear", limit_direction="forward"
            )
            df_merged[price_col] = (
                (df_merged[ratio_col] * df_merged["mnb_index"]).round().astype("Int64")
            )

            df_merged = df_merged.drop(columns=[ratio_col])

    df_merged = df_merged.drop(columns=["mnb_index"])

    return df_merged
