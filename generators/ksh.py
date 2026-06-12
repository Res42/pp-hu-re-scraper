from pathlib import Path
from typing import Generator, List, Tuple

import pandera as pa
from slugify import slugify

from models.ksh import EGYUTT, KshIngatlanAdatSchema, KshPropertyType
from models.pp import PortfolioPerformanceQuote, pp_dump

c = KshIngatlanAdatSchema


def _get_megye_quotes(
    df_all: pa.typing.DataFrame[KshIngatlanAdatSchema],
) -> Generator[Tuple[Path, List[PortfolioPerformanceQuote]], None, None]:
    df_megyek = df_all[df_all[c.szint] == 1]

    for megye_nev, df_megye in df_megyek.groupby(c.megye_nev):
        for tipus, c_ar in KshPropertyType:
            df_megye_with_ar = df_megye.dropna(subset=[c_ar]).sort_values(by=c.ev)

            quotes = [
                PortfolioPerformanceQuote(date=f"{ev}-12-31", value=int(ar))
                for ev, ar in zip(df_megye_with_ar[c.ev], df_megye_with_ar[c_ar])
            ]

            file_path = Path(slugify(str(megye_nev))) / f"{slugify(tipus)}.json"

            yield file_path, quotes


def _get_telepules_quotes(
    df_all: pa.typing.DataFrame[KshIngatlanAdatSchema],
):
    df_telepulesek = df_all[df_all[c.kozter] == EGYUTT]

    for (megye_nev, telepules_nev), df_telepules in df_telepulesek.groupby(
        [c.megye_nev, c.telepules_nev]
    ):
        for tipus, c_ar in KshPropertyType:
            df_telepules_with_ar = df_telepules.dropna(subset=[c_ar]).sort_values(
                by=c.ev
            )

            quotes = [
                PortfolioPerformanceQuote(date=f"{ev}-12-31", value=int(ar))
                for ev, ar in zip(
                    df_telepules_with_ar[c.ev], df_telepules_with_ar[c_ar]
                )
            ]

            file_path = (
                Path(slugify(str(megye_nev)))
                / slugify(str(telepules_nev))
                / f"{slugify(tipus)}.json"
            )

            yield file_path, quotes


def _get_utca_quotes(
    df_all: pa.typing.DataFrame[KshIngatlanAdatSchema],
):
    df_kozteruletek = df_all[(df_all[c.kozter].notna()) & (df_all[c.kozter] != EGYUTT)]

    for (megye_nev, telepules_nev, kozter), df_kozterulet in df_kozteruletek.groupby(
        [c.megye_nev, c.telepules_nev, c.kozter]
    ):
        for tipus, c_ar in KshPropertyType:
            df_kozterulet_with_ar = df_kozterulet.dropna(subset=[c_ar]).sort_values(
                by=c.ev
            )

            quotes = [
                PortfolioPerformanceQuote(date=f"{ev}-12-31", value=int(ar))
                for ev, ar in zip(
                    df_kozterulet_with_ar[c.ev], df_kozterulet_with_ar[c_ar]
                )
            ]

            file_path = (
                Path(slugify(str(megye_nev)))
                / slugify(str(telepules_nev))
                / slugify(str(kozter))
                / f"{slugify(tipus)}.json"
            )

            yield file_path, quotes


def generate_ksh(
    df: pa.typing.DataFrame[KshIngatlanAdatSchema],
    output_base_dir: Path,
) -> None:
    """
    Legenerálja a tiszta (nem extrapolált) KSH JSON mikrofájlokat.
    """
    print("KSH fájlok generálása...")

    # --- 1) MEGYE SZINTŰ FÁJLOK ---
    print("Megye szintű fájlok mentése...")
    for file_path, quotes in _get_megye_quotes(df):
        pp_dump(output_base_dir / file_path, quotes)

    # --- 2) TELEPÜLÉS SZINTŰ FÁJLOK ---
    print("Település szintű fájlok mentése...")
    for file_path, quotes in _get_telepules_quotes(df):
        pp_dump(output_base_dir / file_path, quotes)

    # --- 3) UTCA SZINTŰ FÁJLOK ---
    print("Utca szintű fájlok mentése...")
    for file_path, quotes in _get_utca_quotes(df):
        pp_dump(output_base_dir / file_path, quotes)

    print("KSH fájlok generálása befejeződött.")
