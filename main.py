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

    # 2026-06-12-ei futások megfigyelése alapján; mivel ez évente változhat,
    # ezért néha lehet érdemes frissíteni ezt (de nem törik el, ha nincs frissítve)
    # [megye, település, közterület] iterációs számok
    totals = [80, 8172, 51060]

    with tqdm(desc="Adatforrások letöltése", total=2) as pbar:
        if args.dev:
            with open("data/inga-data.json", "r", encoding="utf-8") as f:
                ksh_raw_data = json.load(f)
                pbar.update(1)
            with open("data/inga-meta.json", "r", encoding="utf-8") as f:
                ksh_metadata = json.load(f)
                pbar.update(1)
        else:
            ksh_raw_data = download_ksh_ingatlan_adattar()
            pbar.update(1)
            ksh_metadata = download_ksh_ingatlan_adattar_metadata()
            pbar.update(1)
            # mnb_lakasarindex = download_mnb_lakasarindex()

    df_all = get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata)

    for file_path, c_ar, df in tqdm(
        get_megye_dfs(df_all), desc="Megye szintű fájlok mentése", total=totals[0]
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    for file_path, c_ar, df in tqdm(
        get_telepules_dfs(df_all),
        desc="Település szintű fájlok mentése",
        total=totals[1],
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    for file_path, c_ar, df in tqdm(
        get_utca_dfs(df_all), desc="Utca szintű fájlok mentése", total=totals[2]
    ):
        ksh = points(df, c_ar)
        ksh_linear = linear_interpolation(df, c_ar)

        if not args.dry_run:
            pp_dump(base_path / "ksh" / file_path, ksh)
            pp_dump(base_path / "ksh-linear" / file_path, ksh_linear)

    print("A fájlok elkészültek.")


if __name__ == "__main__":
    main()
