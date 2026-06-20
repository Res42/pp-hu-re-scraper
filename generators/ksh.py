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
    if df_filtered.empty:
        return

    df_filtered["formatted_date"] = df_filtered[c.datum].dt.strftime("%Y-%m-%d")

    type_columns = KshPropertyType.cols()
    col_to_filename = KshPropertyType.col_file_name_dict()

    df_melted = df_filtered.melt(
        id_vars=group_by + ["formatted_date"],
        value_vars=type_columns,
        var_name="property_type",
        value_name="price",
    )

    df_melted = df_melted.dropna(subset=["price"])
    if df_melted.empty:
        return

    df_melted["price"] = df_melted["price"].astype(int)

    extended_groupby = group_by + ["property_type"]

    for key, df_grouped in df_melted.groupby(extended_groupby):
        if isinstance(key, tuple):
            slugs = list(key[:-1])
            prop_type = key[-1]
        else:
            slugs = [key]
            prop_type = key

        file_name = col_to_filename[prop_type]
        file_path = Path(*slugs) / file_name

        data = [
            {"date": date, "price": price}
            for date, price in zip(df_grouped["formatted_date"], df_grouped["price"])
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
