import argparse
import json
import warnings
from pathlib import Path

from rich.panel import Panel
from tqdm.rich import tqdm

from datasources.ksh import (
    download_ksh_ingatlan_adattar,
    download_ksh_ingatlan_adattar_metadata,
    get_ksh_ingatlan_adattar_data,
)
from datasources.mnb import download_mnb_lakasarindex, get_mnb_lakasarindex
from generators.interpolation import linear_interpolation
from generators.ksh import get_megye_dfs, get_telepules_dfs, get_utca_dfs
from models.console import console
from models.pp import pp_writer

warnings.filterwarnings("ignore", message=".*rich is experimental.*")


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
    parser.add_argument(
        "--zip",
        action="store_true",
        help="If set it will zip the folder structure.",
    )

    args = parser.parse_args()

    base_path = Path(args.output)

    # 2026-06-16-ai futások megfigyelése alapján; mivel ez évente változhat,
    # ezért néha lehet érdemes frissíteni ezt (de nem törik el, ha nincs frissítve)
    # [megye, település, közterület] iterációs számok
    totals = [80, 4854, 26350]

    console.print(Panel("Inicializáció"))

    with tqdm(desc="Adatforrások letöltése", total=3) as pbar:
        if args.dev:
            with open("data/inga-data.json", "r", encoding="utf-8") as f:
                ksh_raw_data = json.load(f)
                pbar.update(1)
            with open("data/inga-meta.json", "r", encoding="utf-8") as f:
                ksh_metadata = json.load(f)
                pbar.update(1)
            with open("data/MNB_lakasarindex_2025Q4.xlsx", "rb") as f:
                mnb_lakasarindex = f.read()
                pbar.update(1)
        else:
            ksh_raw_data = download_ksh_ingatlan_adattar()
            pbar.update(1)
            ksh_metadata = download_ksh_ingatlan_adattar_metadata()
            pbar.update(1)
            mnb_lakasarindex = download_mnb_lakasarindex()
            pbar.update(1)

    df_ksh = get_ksh_ingatlan_adattar_data(ksh_raw_data, ksh_metadata)
    df_mnb = get_mnb_lakasarindex(mnb_lakasarindex)

    series = [
        (Path("ksh"), lambda: df_ksh),
        (Path("ksh-linear"), lambda: linear_interpolation(df_ksh)),
    ]

    with pp_writer(
        args.zip, base_dir=base_path, zip_name="ingatlan_adatok.zip"
    ) as writer:
        for series_path, compute_df in series:
            console.print()
            console.print(Panel(f"{series_path} adatsor"))

            df = compute_df()
            for file_path, data in tqdm(
                get_megye_dfs(df),
                desc="Megye szintű fájlok mentése",
                total=totals[0],
            ):
                if not args.dry_run:
                    writer.dump(series_path / file_path, data)

            for file_path, data in tqdm(
                get_telepules_dfs(df),
                desc="Település szintű fájlok mentése",
                total=totals[1],
            ):
                if not args.dry_run:
                    writer.dump(series_path / file_path, data)

            for file_path, data in tqdm(
                get_utca_dfs(df), desc="Utca szintű fájlok mentése", total=totals[2]
            ):
                if not args.dry_run:
                    writer.dump(series_path / file_path, data)


if __name__ == "__main__":
    main()
