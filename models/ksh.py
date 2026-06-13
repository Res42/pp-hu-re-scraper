from enum import Enum

import pandas as pd
import pandera.pandas as pa

EGYUTT = "együtt"


class TelepulesTipus(int, Enum):
    MEGYE = 0
    BUDAPEST = 1
    MEGYESZEKHELY = 2
    VAROS = 3
    KOZSEG = 4
    BUDAPEST_KERULET = 5


class KshIngatlanAdatSchema(pa.DataFrameModel):
    megye: str = pa.Field()
    """Megye azonosító (feloldás a metadata-ból)"""
    megye_nev: str = pa.Field()
    telaz: str = pa.Field()
    """Település azonosító (feloldás a metadata-ból)"""
    telepules_nev: str = pa.Field()
    tipus: int = pa.Field(isin=TelepulesTipus)
    szint: int = pa.Field()
    """1 = Megye / Budapest, 2 = Települések / budapesti kerületek, 3 = közterület"""
    kozter: str = pa.Field(nullable=True)
    """a konkrét köztér neve, pl: "Almafa utca"; van egy különleges köztér, az "együtt", ami a csoporton belüli összegző footer sor; ha a szint 1-es, akkor nincs megadva"""
    ev: int = pa.Field()
    """év, pl: 2024"""
    datum: pd.Timestamp = pa.Field(coerce=True)
    cshaz_ar: int = pa.Field(nullable=True, coerce=True)
    cshaz_db: int = pa.Field(nullable=True)
    tobbl_ar: int = pa.Field(nullable=True, coerce=True)
    tobbl_db: int = pa.Field(nullable=True)
    panel_ar: int = pa.Field(nullable=True, coerce=True)
    panel_db: int = pa.Field(nullable=True)
    total_ar: int = pa.Field(coerce=True)
    total_db: int = pa.Field()
    szoras: int = pa.Field()
    idosor: int = pa.Field()
    """nem releváns; megjelenik-e a grafikon gomb a KSH felületén"""

    class Config:
        strict = True
        coerce = True


IngatlanDataFrame = pa.typing.DataFrame[KshIngatlanAdatSchema]
c = KshIngatlanAdatSchema


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
