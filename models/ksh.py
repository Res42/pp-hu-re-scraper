from enum import Enum

import pandera.pandas as pa

EGYUTT = "együtt"


class KshIngatlanAdatSchema(pa.DataFrameModel):
    megye: str = pa.Field()
    """Megye azonosító (feloldás a metadata-ból)"""
    megye_nev: str = pa.Field()
    telaz: str = pa.Field()
    """Település azonosító (feloldás a metadata-ból)"""
    telepules_nev: str = pa.Field()
    szint: int = pa.Field()
    """1 = Megye / Budapest, 2 = Települések / budapesti kerületek, 3 = közterület"""
    kozter: str = pa.Field(nullable=True)
    """a konkrét köztér neve, pl: "Almafa utca"; van egy különleges köztér, az "együtt", ami a csoporton belüli összegző footer sor; ha a szint 1-es, akkor nincs megadva"""
    ev: int = pa.Field()
    """év, pl: 2024"""
    cshaz_ar: int = pa.Field(nullable=True)
    cshaz_db: int = pa.Field(nullable=True)
    tobbl_ar: int = pa.Field(nullable=True)
    tobbl_db: int = pa.Field(nullable=True)
    panel_ar: int = pa.Field(nullable=True)
    panel_db: int = pa.Field(nullable=True)
    total_ar: int = pa.Field()
    total_db: int = pa.Field()
    szoras: int = pa.Field()
    idosor: int = pa.Field()
    """nem releváns; megjelenik-e a grafikon gomb a KSH felületén"""

    class Config:
        strict = True
        coerce = True


class KshPropertyType(Enum):
    """Ingatlan típus és ár oszlop párosok."""

    CSHAZ = ("cshaz", "cshaz_ar")
    PANEL = ("panel", "panel_ar")
    TOBBL = ("tobbl", "tobbl_ar")
    TOTAL = ("total", "total_ar")

    def __init__(self, type: str, price_col_name: str) -> None:
        self.type: str = type
        self.price_col_name: str = price_col_name

    def __iter__(self):
        return iter((self.type, self.price_col_name))
