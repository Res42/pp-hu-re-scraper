import argparse
import itertools
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
from models.console import console
from pipeline.group import group_by_file, map_group
from pipeline.interpolation import grouped_linear_interpolation
from pipeline.json import pp_writer, save_groups
from pipeline.mnb import add_mnb_to_ksh

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
        "--local",
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
    total = 31284

    console.print(Panel("Inicializáció"))

    with tqdm(desc="Adatforrások letöltése", total=5) as pbar:
        if args.local:
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
        pbar.update(1)
        df_mnb = get_mnb_lakasarindex(mnb_lakasarindex)
        pbar.update(1)

    with pp_writer(
        args.zip, args.dry_run, base_dir=base_path, zip_name="ingatlan_adatok.zip"
    ) as writer:
        base_stream = group_by_file(df_ksh)
        stream1, stream2, stream3 = itertools.tee(base_stream, 3)

        series = [
            (
                "ksh",
                stream1,
                [save_groups(Path("ksh"), total=total, writer=writer)],
            ),
            (
                "ksh-linear",
                stream2,
                [
                    map_group(grouped_linear_interpolation),
                    save_groups(Path("ksh-linear"), total=total, writer=writer),
                ],
            ),
            (
                "ksh-mnb-linear",
                stream3,
                [
                    map_group(add_mnb_to_ksh(df_mnb)),
                    map_group(grouped_linear_interpolation),
                    save_groups(Path("ksh-mnb-linear"), total=total, writer=writer),
                ],
            ),
        ]

        for name, df, transformers in series:
            console.print()
            console.print(Panel(f"{name} adatsor"))

            result = df
            for transform in transformers:
                result = transform(result)


if __name__ == "__main__":
    main()
