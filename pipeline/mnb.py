import polars as pl

from models.ksh import IngatlanArDataFrame, IngatlanMetadata, TelepulesTipus, ca
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


def _get_mnb_column(metadata: IngatlanMetadata) -> str:
    tipus = metadata.telepules_tipus
    megye_kod = metadata.megye

    if (
        tipus in [TelepulesTipus.BUDAPEST, TelepulesTipus.BUDAPEST_KERULET]
        or megye_kod == "01"
    ):
        return m.budapest
    if tipus == TelepulesTipus.KOZSEG:
        return m.kozsegek
    return _MEGYE_REGIO_MAP.get(megye_kod, m.varosok)


def add_mnb_to_ksh(df_mnb: MnbDataFrame):
    def operator(
        df: IngatlanArDataFrame, metadata: IngatlanMetadata
    ) -> IngatlanArDataFrame:
        if df.is_empty():
            return df

        mnb_col_name = _get_mnb_column(metadata)
        min_date = df.select(pl.col(ca.date).min()).item()

        df_mnb_skeleton = df_mnb.select(
            [
                pl.col(m.datum).alias(ca.date),
                pl.col(mnb_col_name).alias("mnb_index"),
            ]
        ).filter(pl.col(ca.date) >= min_date)

        df = df.set_sorted(ca.date)
        df_mnb_skeleton = df_mnb_skeleton.set_sorted(ca.date)

        df = df.join(df_mnb_skeleton, on=ca.date, how="right")

        ratio_expr = pl.col(ca.price).cast(pl.Float64) / pl.col("mnb_index")

        df = df.with_columns(
            (ratio_expr.interpolate().forward_fill() * pl.col("mnb_index"))
            .round(0)
            .cast(pl.Int64)
            .alias(ca.price)
        ).drop("mnb_index")

        return df

    return operator
