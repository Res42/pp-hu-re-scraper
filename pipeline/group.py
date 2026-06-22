from collections.abc import Callable, Iterator

from models.ksh import IngatlanDataFrame, c


def group_by_file(df: IngatlanDataFrame) -> Iterator[tuple[str, IngatlanDataFrame]]:
    for (output_path,), df_file in df.group_by(c.output_path):
        yield output_path, df_file


def map_group(fn: Callable[[IngatlanDataFrame], IngatlanDataFrame]):
    def operator(
        source_iterator: Iterator[tuple[str, IngatlanDataFrame]],
    ) -> Iterator[tuple[str, IngatlanDataFrame]]:
        for output_path, df_file in source_iterator:
            yield output_path, fn(df_file)

    return operator
