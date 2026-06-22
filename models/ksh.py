from dataclasses import dataclass
from datetime import date
from enum import IntEnum, StrEnum
from typing import Optional

import patito as pt
import polars as pl
from pydantic import BaseModel
from slugify import slugify

EGYUTT = "együtt"


class IngatlanTipus(StrEnum):
    CSHAZ = ("cshaz", "cshaz_ar")
    PANEL = ("panel", "panel_ar")
    TOBBL = ("tobbl", "tobbl_ar")
    TOTAL = ("total", "total_ar")

    def __new__(cls, type_str: str, price_col_name: str):
        # Ez a trükk biztosítja, hogy az Enum tag értéke (value) a tiszta string legyen (pl. "cshaz")
        obj = str.__new__(cls, type_str)
        obj._value_ = type_str

        obj.type = type_str
        obj.price_col_name = price_col_name
        obj.file_name = f"{slugify(type_str)}.json"
        return obj

    @staticmethod
    def price_cols():
        return [t.price_col_name for t in IngatlanTipus]

    @staticmethod
    def col_file_name_dict():
        return {t.price_col_name: t.file_name for t in IngatlanTipus}

    @staticmethod
    def col_to_type_dict():
        return {t.price_col_name: t.type for t in IngatlanTipus}


class TelepulesTipus(IntEnum):
    MEGYE = 0
    BUDAPEST = 1
    MEGYESZEKHELY = 2
    VAROS = 3
    KOZSEG = 4
    BUDAPEST_KERULET = 5


class KshIngatlanAdatSchema(pt.Model):
    megye: str
    """Megye azonosító (feloldás a metadata-ból)"""
    telaz: str
    """Település azonosító (feloldás a metadata-ból)"""
    telepules_tipus: int = pt.Field(
        constraints=pt.field.is_in([e.value for e in TelepulesTipus]),
    )
    szint: int
    """1 = Megye / Budapest, 2 = Települések / budapesti kerületek, 3 = közterület"""
    kozter: Optional[str] = None
    """a konkrét köztér neve, pl: "Almafa utca"; van egy különleges köztér, az "együtt", ami a csoporton belüli összegző footer sor; ha a szint 1-es, akkor nincs megadva"""
    ev: int
    datum: date
    ingatlan_tipus: IngatlanTipus
    ar: int
    output_path: str


@dataclass(frozen=True)
class KshIngatlanAdatSchemaCols:
    megye = "megye"
    telaz = "telaz"
    telepules_tipus = "telepules_tipus"
    ev = "ev"
    datum = "datum"
    ingatlan_tipus = "ingatlan_tipus"
    ar = "ar"
    output_path = "output_path"


IngatlanDataFrame = pt.DataFrame[KshIngatlanAdatSchema]
c = KshIngatlanAdatSchemaCols()


class IngatlanArSchema(pt.Model):
    date: date
    price: int


@dataclass(frozen=True)
class IngatlanArSchemaCols:
    date = "date"
    price = "price"


IngatlanArDataFrame = pt.DataFrame[IngatlanArSchema]
ca = IngatlanArSchemaCols()


class IngatlanMetadata(BaseModel):
    megye: str
    telaz: str
    telepules_tipus: TelepulesTipus
    szint: int
    kozter: Optional[str]
    ev: int
    ingatlan_tipus: IngatlanTipus


KSH_RAW_INPUT_SCHEMA = {
    "megye": pl.String,
    "telaz": pl.String,
    "szint": pl.Int64,
    "kozter": pl.String,
    "ev": pl.Int64,
    "szoras": pl.Float64,
    "idosor": pl.String,
    "cshaz_ar": pl.Int64,
    "tobbl_ar": pl.Int64,
    "panel_ar": pl.Int64,
    "total_ar": pl.Int64,
    "cshaz_db": pl.Int64,
    "tobbl_db": pl.Int64,
    "panel_db": pl.Int64,
    "total_db": pl.Int64,
}


@dataclass(frozen=True)
class KshRawColumns:
    megye = "megye"
    telaz = "telaz"
    szint = "szint"
    kozter = "kozter"
    ev = "ev"
    szoras = "szoras"
    idosor = "idosor"
    cshaz_ar = "cshaz_ar"
    tobbl_ar = "tobbl_ar"
    panel_ar = "panel_ar"
    total_ar = "total_ar"
    cshaz_db = "cshaz_db"
    tobbl_db = "tobbl_db"
    panel_db = "panel_db"
    total_db = "total_db"


cr = KshRawColumns()

MEGYE_FILTER = pl.col(cr.szint) == 1
TELEPULES_FILTER = (pl.col(cr.szint) != 1) & (pl.col(cr.kozter) == EGYUTT)
UTCA_FILTER = (
    (pl.col(cr.szint) != 1)
    & (pl.col(cr.kozter).is_not_null())
    & (pl.col(cr.kozter) != EGYUTT)
)
