import argparse
import json
from pathlib import Path

from tqdm import tqdm

from datasources.ksh import (
    download_ksh_ingatlan_adattar,
    download_ksh_ingatlan_adattar_metadata,
    get_ksh_ingatlan_adattar_data,
)
from generators.interpolation import linear_interpolation, points
from generators.ksh import get_megye_dfs, get_telepules_dfs, get_utca_dfs
from models.pp import pp_dump


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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set it will not write to files.",
    )

    args = parser.parse_args()

    base_path = Path(args.output)

    print("Adatforrások letöltése...")

    if args.dev:
        with open("data/inga-data.json", "r", encoding="utf-8") as f:
            ksh_raw_data = json.load(f)
        with open("data/inga-meta.json", "r", encoding="utf-8") as f:
            ksh_metadata = json.load(f)
    else:
        ksh_raw_data = download_ksh_ingatlan_adattar()
        ksh_metadata = download_ksh_ingatlan_adattar_metadata()
        # mnb_lakasarindex = download_mnb_lakasarindex()

    print("Adatforrások letöltése sikeres.")

    df_all = get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata)

    for file_path, c_ar, df in tqdm(
        get_megye_dfs(df_all), desc="Megye szintű fájlok mentése"
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    for file_path, c_ar, df in tqdm(
        get_telepules_dfs(df_all), desc="Település szintű fájlok mentése"
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    for file_path, c_ar, df in tqdm(
        get_utca_dfs(df_all), desc="Utca szintű fájlok mentése"
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    print("A fájlok elkészültek.")


if __name__ == "__main__":
    main()
