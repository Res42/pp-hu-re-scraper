import polars as pl

from models.ksh import IngatlanDataFrame, c


def linear_interpolation(df: IngatlanDataFrame) -> IngatlanDataFrame:
    df = df.sort([c.output_path, c.datum])

    df = df.upsample(time_column=c.datum, by=c.output_path, every="1d")

    df = df.with_columns([pl.col(c.ar).interpolate().over(c.output_path).alias(c.ar)])

    metadata_cols = [
        col for col in df.columns if col not in [c.ar, c.datum, c.output_path]
    ]

    if metadata_cols:
        df = df.with_columns(
            [
                pl.col(col)
                .forward_fill()
                .backward_fill()
                .over(c.output_path)
                .alias(col)
                for col in metadata_cols
            ]
        )

    df = df.with_columns(pl.col(c.ar).round(0).cast(pl.Int64).alias(c.ar))

    return df


def grouped_linear_interpolation(df: IngatlanDataFrame) -> IngatlanDataFrame:
    df = df.sort([c.datum])

    df = df.upsample(time_column=c.datum, every="1d")

    df = df.with_columns([pl.col(c.ar).interpolate().alias(c.ar)])

    metadata_cols = [col for col in df.columns if col not in [c.ar, c.datum]]

    if metadata_cols:
        df = df.with_columns(
            [
                pl.col(col).forward_fill().backward_fill().alias(col)
                for col in metadata_cols
            ]
        )

    df = df.with_columns(pl.col(c.ar).round(0).cast(pl.Int64).alias(c.ar))

    return df
