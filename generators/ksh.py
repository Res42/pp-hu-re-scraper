from collections.abc import Iterator
from pathlib import Path

from slugify import slugify

from models.ksh import (
    EGYUTT,
    IngatlanDataFrame,
    KshPropertyType,
    c,
)


def get_megye_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    df_megyek = df_all[df_all[c.szint] == 1]

    for megye_nev, df_megye in df_megyek.groupby(c.megye_nev):
        for tipus, c_ar in KshPropertyType:
            df_megye_with_ar = df_megye.dropna(subset=[c_ar])

            file_path = Path(slugify(str(megye_nev))) / f"{slugify(tipus)}.json"

            yield file_path, c_ar, df_megye_with_ar


def get_telepules_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    df_telepulesek = df_all[df_all[c.kozter] == EGYUTT]

    for (megye_nev, telepules_nev), df_telepules in df_telepulesek.groupby(
        [c.megye_nev, c.telepules_nev]
    ):
        for tipus, c_ar in KshPropertyType:
            df_telepules_with_ar = df_telepules.dropna(subset=[c_ar])
            file_path = (
                Path(slugify(str(megye_nev)))
                / slugify(str(telepules_nev))
                / f"{slugify(tipus)}.json"
            )
            yield file_path, c_ar, df_telepules_with_ar


def get_utca_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    df_kozteruletek = df_all[(df_all[c.kozter].notna()) & (df_all[c.kozter] != EGYUTT)]

    for (megye_nev, telepules_nev, kozter), df_kozterulet in df_kozteruletek.groupby(
        [c.megye_nev, c.telepules_nev, c.kozter]
    ):
        for tipus, c_ar in KshPropertyType:
            df_kozterulet_with_ar = df_kozterulet.dropna(subset=[c_ar])
            file_path = (
                Path(slugify(str(megye_nev)))
                / slugify(str(telepules_nev))
                / slugify(str(kozter))
                / f"{slugify(tipus)}.json"
            )
            yield file_path, c_ar, df_kozterulet_with_ar
