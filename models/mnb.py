from dataclasses import dataclass
from datetime import date
from typing import Optional

import patito as pt


class MnbLakasarindexSchema(pt.Model):
    datum: date

    aggregated: float
    budapest: Optional[float] = None
    varosok: Optional[float] = None
    varosok_del_alfold: Optional[float] = None
    varosok_del_dunantul: Optional[float] = None
    varosok_eszak_alfold: Optional[float] = None
    varosok_eszak_magyarorszag: Optional[float] = None
    varosok_kozep_dunantul: Optional[float] = None
    varosok_pest: Optional[float] = None
    varosok_nyugat_dunantul: Optional[float] = None
    kozsegek: Optional[float] = None


@dataclass(frozen=True)
class MnbLakasarindexSchemaCols:
    datum = "datum"
    aggregated = "aggregated"
    budapest = "budapest"
    varosok = "varosok"
    varosok_del_alfold = "varosok_del_alfold"
    varosok_del_dunantul = "varosok_del_dunantul"
    varosok_eszak_alfold = "varosok_eszak_alfold"
    varosok_eszak_magyarorszag = "varosok_eszak_magyarorszag"
    varosok_kozep_dunantul = "varosok_kozep_dunantul"
    varosok_pest = "varosok_pest"
    varosok_nyugat_dunantul = "varosok_nyugat_dunantul"
    kozsegek = "kozsegek"


MnbDataFrame = pt.DataFrame[MnbLakasarindexSchema]
m = MnbLakasarindexSchemaCols()
