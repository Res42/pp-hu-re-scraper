import json
from pathlib import Path
from typing import List

from pydantic import BaseModel


class PortfolioPerformanceQuote(BaseModel):
    date: str
    """YYYY-MM-DD"""
    price: int
    """Ft/m²"""


def pp_to_json(quotes: List[PortfolioPerformanceQuote]):
    return [q.model_dump() for q in quotes]


def pp_dump(file_path: Path, quotes: List[PortfolioPerformanceQuote]):
    if not len(quotes):
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(pp_to_json(quotes), f, indent=2)
