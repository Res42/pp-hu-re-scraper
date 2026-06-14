import numpy as np
import pandas as pd

from models.ksh import IngatlanDataFrame, c
from models.pp import PortfolioPerformanceQuotes


def points(df: IngatlanDataFrame, c_ar: str) -> PortfolioPerformanceQuotes:
    df_output = pd.DataFrame(
        {"date": df[c.datum].dt.strftime("%Y-%m-%d"), "price": df[c_ar].astype(int)}
    )

    return df_output.to_dict(orient="records")


def linear_interpolation(
    df: IngatlanDataFrame, c_ar: str
) -> PortfolioPerformanceQuotes:
    # Ha nincs elég adatpont, nem tudunk interpolálni
    if len(df) < 2:
        return points(df, c_ar)

    sorted_df = df[[c.datum, c_ar]].sort_values(by=c.datum)

    raw_dates = sorted_df[c.datum].values
    raw_prices = sorted_df[c_ar].values.astype(float)

    start_date = raw_dates[0]
    end_date = raw_dates[-1]

    daily_dates = np.arange(
        start_date, end_date + np.timedelta64(1, "D"), np.timedelta64(1, "D")
    )

    xp = raw_dates.astype("datetime64[D]").astype(float)
    x = daily_dates.astype("datetime64[D]").astype(float)

    interp_prices = np.interp(x, xp, raw_prices).round().astype(int)

    date_strs = daily_dates.astype("datetime64[D]").astype(str)

    return [{"date": d, "price": int(p)} for d, p in zip(date_strs, interp_prices)]
