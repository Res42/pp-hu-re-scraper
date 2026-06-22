import polars as pl

from models.ksh import IngatlanArDataFrame, IngatlanMetadata, ca


def grouped_linear_interpolation(
    df: IngatlanArDataFrame, metadata: IngatlanMetadata
) -> IngatlanArDataFrame:
    df = df.sort([ca.date])

    df = df.upsample(time_column=ca.date, every="1d")

    df = df.with_columns(
        pl.col(ca.price).interpolate().round(0).cast(pl.Int64).alias(ca.price)
    )

    return df
