import polars as pl

from models.ksh import IngatlanDataFrame, c
from models.mnb import m

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


def _get_mnb_column_expr() -> pl.Expr:
    megye_cond = pl.when(pl.col(c.megye) == "01").then(pl.lit(m.budapest))
    for megye_kod, mnb_col in _MEGYE_REGIO_MAP.items():
        megye_cond = megye_cond.when(pl.col(c.megye) == megye_kod).then(pl.lit(mnb_col))
    megye_cond = megye_cond.otherwise(pl.lit(m.varosok))
    return megye_cond


def add_mnb_to_ksh(df_mnb: pl.DataFrame):
    def operator(df: IngatlanDataFrame) -> IngatlanDataFrame:
        if df.is_empty():
            return df

        mnb_col_name = df.select(_get_mnb_column_expr()).item(0, 0)
        min_date = df[c.datum].min()

        df_mnb_skeleton = pl.DataFrame(
            df_mnb.filter(pl.col(m.datum) >= min_date).select(
                [
                    pl.col(m.datum).alias(c.datum),
                    pl.col(mnb_col_name).alias("mnb_index"),
                ]
            )
        )

        df = df.join(df_mnb_skeleton, on=c.datum, how="right")

        metadata_cols = [
            col for col in df.columns if col not in [c.ar, c.datum, "mnb_index"]
        ]
        if metadata_cols:
            df = df.with_columns(
                [pl.col(col).forward_fill().backward_fill() for col in metadata_cols]
            )

        if c.ar in df.columns and df[c.ar].null_count() < len(df):
            ratio_expr = pl.col(c.ar).cast(pl.Float64) / pl.col("mnb_index").cast(
                pl.Float64
            )

            df = df.with_columns(
                (ratio_expr.interpolate().forward_fill() * pl.col("mnb_index"))
                .round(0)
                .cast(pl.Int64)
                .alias(c.ar)
            )

        return df.drop("mnb_index")

    return operator
