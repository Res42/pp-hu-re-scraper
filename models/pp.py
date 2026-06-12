import json
from pathlib import Path

PortfolioPerformanceQuotes = list[dict]


def pp_dump(file_path: Path, quotes: PortfolioPerformanceQuotes):
    if not len(quotes):
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2)
