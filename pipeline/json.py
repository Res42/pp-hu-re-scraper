import contextlib
import zipfile
from pathlib import Path
from typing import Iterable

import orjson
from tqdm.rich import tqdm

from models.ksh import IngatlanArDataFrame, IngatlanMetadata

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

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as z:
            yield ZipWriter(z)
    else:
        yield DiskWriter(base_path=base_dir)


def save_groups(
    series_path: Path, total: int, writer: NoOpWriter | ZipWriter | DiskWriter
):
    def operator(
        source_iterator: Iterable[tuple[str, IngatlanMetadata, IngatlanArDataFrame]],
    ) -> None:
        for output_path, metadata, df in tqdm(
            source_iterator, desc="Fájlok mentése", total=total
        ):
            writer.dump(series_path / output_path, df.to_dicts())

    return operator
