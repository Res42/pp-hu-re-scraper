import time

import pandas as pd

from generators.ksh import (
    KOZTERULET_GROUP_BY,
    MEGYE_GROUP_BY,
    TELEPULES_GROUP_BY,
    get_megye_mask,
    get_telepules_mask,
    get_utca_mask,
)
from models.console import console
from models.ksh import IngatlanDataFrame, c

_INTERPOLATED_COLS = [c.cshaz_ar, c.panel_ar, c.tobbl_ar, c.total_ar]

_INTERPOLATION_LEVELS = [
    (get_megye_mask, MEGYE_GROUP_BY, "Megye"),
    (get_telepules_mask, TELEPULES_GROUP_BY, "Település"),
    (get_utca_mask, KOZTERULET_GROUP_BY, "Utca"),
]


def linear_interpolation(df: IngatlanDataFrame) -> IngatlanDataFrame:
    df = df.copy()
    interpolated_chunks = []

    # Elindítjuk a globális státusz kijelzést a te console objektumoddal
    with console.status(
        "[bold green]Napi szintű interpoláció kiszámítása...[/bold green]",
        spinner="dots",
    ):
        for get_mask, group_cols, level_name in _INTERPOLATION_LEVELS:
            mask = get_mask(df)
            level_df = df[mask]

            if level_df.empty:
                console.print(f"[yellow]![/yellow] {level_name} szint üres, kihagyás.")
                continue

            grouped = level_df.groupby(group_cols)
            group_count = len(grouped)

            start_time = time.time()
            level_processed_groups = []

            for keys, group in grouped:
                # 1. Idősoros index beállítása
                group_indexed = group.set_index(c.datum)

                # 2. Átmintavételezés napi szintre
                resampled_group = group_indexed.resample("D").asfreq()

                # 3. Lineáris interpoláció végrehajtása
                resampled_group[_INTERPOLATED_COLS] = resampled_group[
                    _INTERPOLATED_COLS
                ].interpolate(method="linear", limit_direction="both")

                # 4. Nem numerikus oszlopok kitöltése
                non_numeric_cols = [
                    col
                    for col in group_indexed.columns
                    if col not in _INTERPOLATED_COLS
                ]
                resampled_group[non_numeric_cols] = (
                    resampled_group[non_numeric_cols].ffill().bfill()
                )

                resampled_group = resampled_group.reset_index()

                # Csoportosítási kulcsok visszaírása
                if isinstance(keys, tuple):
                    for col, val in zip(group_cols, keys):
                        resampled_group[col] = val
                else:
                    resampled_group[group_cols] = keys

                level_processed_groups.append(resampled_group)

            if level_processed_groups:
                interpolated_chunks.append(
                    pd.concat(level_processed_groups, ignore_index=True)
                )

            # Az összegző üzenet kiírása – a status spinner ez alatt pörög tovább
            elapsed = time.time() - start_time
            console.print(
                f"[green]✓[/green] {level_name} szint sikeresen interpolálva ({group_count} csoport, {elapsed:.2f}s)."
            )

    # Adatok összefűzése a status kontextuson kívül
    if interpolated_chunks:
        final_df = pd.concat(interpolated_chunks, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=df.columns)

    # Lebegőpontos árak visszakerekítése egész típusra (NaN kompatibilis Int64)
    for col in _INTERPOLATED_COLS:
        final_df[col] = final_df[col].round().astype(pd.Int64Dtype())

    return final_df
