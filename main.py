import argparse
import json
from pathlib import Path

from datasources.ksh import (
    download_ksh_ingatlan_adattar,
    download_ksh_ingatlan_adattar_metadata,
    get_ksh_ingatlan_adattar_data,
)
from generators.ksh import generate_ksh


def main():
    parser = argparse.ArgumentParser(
        description="Hungarian real estate price scraper CLI tool"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="dist",
        help="The output folder to dump the JSON files.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Local resource use (downloaded JSON files) instead of downloading them from remote sources.",
    )

    args = parser.parse_args()

    if args.dev:
        with open("data/inga-data.json", "r", encoding="utf-8") as f:
            ksh_raw_data = json.load(f)
        with open("data/inga-meta.json", "r", encoding="utf-8") as f:
            ksh_metadata = json.load(f)
    else:
        ksh_raw_data = download_ksh_ingatlan_adattar()
        ksh_metadata = download_ksh_ingatlan_adattar_metadata()

    df = get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata)
    generate_ksh(df, Path(args.output) / "ksh")


if __name__ == "__main__":
    main()
