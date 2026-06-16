from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from models.ksh import (
    EGYUTT,
    IngatlanDataFrame,
    KshPropertyType,
    c,
)

MEGYE_GROUP_BY = [c.megye_slug]
TELEPULES_GROUP_BY = [c.megye_slug, c.telepules_slug]
KOZTERULET_GROUP_BY = [c.megye_slug, c.telepules_slug, c.kozter_slug]


def get_megye_mask(df: IngatlanDataFrame) -> pd.Series:
    return df[c.szint] == 1


def get_telepules_mask(df: IngatlanDataFrame) -> pd.Series:
    return (df[c.szint] != 1) & (df[c.kozter] == EGYUTT)


def get_utca_mask(df: IngatlanDataFrame) -> pd.Series:
    return (df[c.szint] != 1) & (df[c.kozter].notna()) & (df[c.kozter] != EGYUTT)


def _get_filtered_dfs(
    df: IngatlanDataFrame, mask: pd.Series, group_by: list[str]
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    df_filtered = df[mask]

    for key, df_grouped in df_filtered.groupby(group_by):
        slugs = list(key) if isinstance(key, tuple) else [key]
        for file_name, c_ar in KshPropertyType:
            df_with_ar = df_grouped.dropna(subset=[c_ar])

            file_path = Path(*slugs) / file_name

            yield file_path, c_ar, df_with_ar


def get_megye_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    return _get_filtered_dfs(df_all, get_megye_mask(df_all), MEGYE_GROUP_BY)


def get_telepules_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    return _get_filtered_dfs(df_all, get_telepules_mask(df_all), TELEPULES_GROUP_BY)


def get_utca_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, str, IngatlanDataFrame]]:
    return _get_filtered_dfs(df_all, get_utca_mask(df_all), KOZTERULET_GROUP_BY)
