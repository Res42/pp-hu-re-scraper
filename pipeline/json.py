import contextlib
import zipfile
from pathlib import Path
from typing import Iterable

import orjson
import polars as pl
from tqdm.rich import tqdm

from models.ksh import IngatlanDataFrame, c

PortfolioPerformanceQuotes = list[dict]


class NoOpWriter:
    def dump(self, file_path: Path, quotes: PortfolioPerformanceQuotes):
        pass


class DiskWriter:
    """Writes directly to disk under a base folder (e.g., 'dist')."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def dump(self, file_path: Path, quotes: PortfolioPerformanceQuotes):
        if not len(quotes):
            return

        full_path = self.base_path / file_path

        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(orjson.dumps(quotes))


class ZipWriter:
    """Writes into a ZIP file (e.g., 'dist/file.zip')."""

    def __init__(self, zip_instance: zipfile.ZipFile):
        self.zip = zip_instance

    def dump(self, file_path: Path, quotes: PortfolioPerformanceQuotes):
        if not len(quotes):
            return

        self.zip.writestr(file_path.as_posix(), orjson.dumps(quotes))


@contextlib.contextmanager
def pp_writer(is_zip: bool, dry_run: bool, base_dir: Path, zip_name: Path):
    if dry_run:
        yield NoOpWriter()
    if is_zip:
        zip_path = base_dir / zip_name
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            yield ZipWriter(z)
    else:
        yield DiskWriter(base_path=base_dir)


def _df_to_pp(df: IngatlanDataFrame) -> PortfolioPerformanceQuotes:
    return df.select(
        pl.struct(
            date=pl.col(c.datum).dt.to_string("%Y-%m-%d"), price=pl.col(c.ar)
        ).alias("json_struct")
    )["json_struct"].to_list()


def save_groups(
    series_path: Path, total: int, writer: NoOpWriter | ZipWriter | DiskWriter
):
    def operator(source_iterator: Iterable[tuple[str, IngatlanDataFrame]]) -> None:
        for output_path, data in tqdm(
            source_iterator, desc="Fájlok mentése", total=total
        ):
            writer.dump(series_path / output_path, _df_to_pp(data))

    return operator
