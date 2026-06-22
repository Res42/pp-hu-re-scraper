from collections.abc import Callable, Iterator

import polars as pl

from models.ksh import IngatlanArDataFrame, IngatlanDataFrame, IngatlanMetadata, c, ca


def group_by_file(
    df: IngatlanDataFrame,
) -> Iterator[tuple[str, IngatlanMetadata, IngatlanArDataFrame]]:
    meta_cols = list(IngatlanMetadata.model_fields.keys())
    partitioned = df.partition_by(c.output_path, as_dict=True)

    for (output_path,), df_file in partitioned.items():
        existing_meta = [col for col in meta_cols if col in df_file.columns]
        raw_meta_dict = df_file.select(existing_meta).row(0, named=True)
        metadata = IngatlanMetadata(**raw_meta_dict)

        df_file = df_file.select(
            [pl.col(c.datum).alias(ca.date), pl.col(c.ar).alias(ca.price)]
        )

        yield output_path, metadata, df_file


def map_group(
    fn: Callable[[IngatlanArDataFrame, IngatlanMetadata], IngatlanArDataFrame],
):
    def operator(
        source_iterator: Iterator[tuple[str, IngatlanMetadata, IngatlanArDataFrame]],
    ) -> Iterator[tuple[str, IngatlanMetadata, IngatlanArDataFrame]]:
        for output_path, metadata, df_file in source_iterator:
            yield output_path, metadata, fn(df_file, metadata)

    return operator
