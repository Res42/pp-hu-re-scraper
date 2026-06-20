from enum import Enum

import pandas as pd
import pandera.pandas as pa
from slugify import slugify

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
    megye_slug: str = pa.Field()
    telaz: str = pa.Field()
    """Település azonosító (feloldás a metadata-ból)"""
    telepules_slug: str = pa.Field()
    tipus: int = pa.Field(isin=TelepulesTipus)
    szint: int = pa.Field()
    """1 = Megye / Budapest, 2 = Települések / budapesti kerületek, 3 = közterület"""
    kozter: str = pa.Field(nullable=True)
    kozter_slug: str = pa.Field(nullable=True)
    """a konkrét köztér neve, pl: "Almafa utca"; van egy különleges köztér, az "együtt", ami a csoporton belüli összegző footer sor; ha a szint 1-es, akkor nincs megadva"""
    ev: int = pa.Field()
    datum: pd.Timestamp = pa.Field(coerce=True)
    cshaz_ar: int = pa.Field(nullable=True, coerce=True)
    tobbl_ar: int = pa.Field(nullable=True, coerce=True)
    panel_ar: int = pa.Field(nullable=True, coerce=True)
    total_ar: int = pa.Field(coerce=True)

    class Config:
        strict = True
        coerce = True


IngatlanDataFrame = pa.typing.DataFrame[KshIngatlanAdatSchema]
c = KshIngatlanAdatSchema


class KshPropertyType(Enum):
    """Ingatlan típus és ár oszlop párosok."""

    CSHAZ = ("cshaz", c.cshaz_ar)
    PANEL = ("panel", c.panel_ar)
    TOBBL = ("tobbl", c.tobbl_ar)
    TOTAL = ("total", c.total_ar)

    def __init__(self, type: str, price_col_name: str) -> None:
        self.type: str = type
        self.price_col_name: str = price_col_name
        self.file_name: str = f"{slugify(type)}.json"

    def __iter__(self):
        return iter((self.file_name, self.price_col_name))

    @staticmethod
    def cols():
        return [t.price_col_name for t in KshPropertyType]

    @staticmethod
    def col_file_name_dict():
        return {t.price_col_name: t.file_name for t in KshPropertyType}
