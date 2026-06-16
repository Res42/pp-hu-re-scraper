from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from models.ksh import (
    EGYUTT,
    IngatlanDataFrame,
    KshPropertyType,
    c,
)
from models.pp import PortfolioPerformanceQuotes

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
) -> Iterator[tuple[Path, PortfolioPerformanceQuotes]]:
    df_filtered = df[mask].copy()

    df_filtered["formatted_date"] = df_filtered[c.datum].dt.strftime("%Y-%m-%d")

    for key, df_grouped in df_filtered.groupby(group_by):
        slugs = list(key) if isinstance(key, tuple) else [key]

        for file_name, c_ar in KshPropertyType:
            df_subset = df_grouped[["formatted_date", c_ar]].dropna(subset=[c_ar])

            if df_subset.empty:
                continue

            file_path = Path(*slugs) / file_name

            data = [
                {"date": date, "price": int(price)}
                for date, price in zip(df_subset["formatted_date"], df_subset[c_ar])
            ]

            yield file_path, data


def get_megye_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, PortfolioPerformanceQuotes]]:
    return _get_filtered_dfs(df_all, get_megye_mask(df_all), MEGYE_GROUP_BY)


def get_telepules_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, PortfolioPerformanceQuotes]]:
    return _get_filtered_dfs(df_all, get_telepules_mask(df_all), TELEPULES_GROUP_BY)


def get_utca_dfs(
    df_all: IngatlanDataFrame,
) -> Iterator[tuple[Path, PortfolioPerformanceQuotes]]:
    return _get_filtered_dfs(df_all, get_utca_mask(df_all), KOZTERULET_GROUP_BY)
