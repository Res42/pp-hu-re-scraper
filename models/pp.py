from pathlib import Path

import orjson

PortfolioPerformanceQuotes = list[dict]


def pp_dump(file_path: Path, quotes: PortfolioPerformanceQuotes):
    if not len(quotes):
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(orjson.dumps(quotes))
