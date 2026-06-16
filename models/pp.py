import contextlib
import zipfile
from pathlib import Path

import orjson
import pandas as pd

from models.ksh import IngatlanDataFrame, c

PortfolioPerformanceQuotes = list[dict]


def to_pp_json(df: IngatlanDataFrame, c_ar: str) -> PortfolioPerformanceQuotes:
    df_output = pd.DataFrame(
        {"date": df[c.datum].dt.strftime("%Y-%m-%d"), "price": df[c_ar].astype(int)}
    )

    return df_output.to_dict(orient="records")


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
def pp_writer(is_zip: bool, base_dir: Path, zip_name: Path):
    if is_zip:
        zip_path = base_dir / zip_name
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            yield ZipWriter(z)
    else:
        yield DiskWriter(base_path=base_dir)
