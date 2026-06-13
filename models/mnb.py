import pandas as pd
import pandera.pandas as pa


class MnbLakasarindexSchema(pa.DataFrameModel):
    quarter: str = pa.Field()
    datum: pd.Timestamp = pa.Field(coerce=True)

    aggregated: float = pa.Field()
    budapest: float = pa.Field(nullable=True, coerce=True)
    varosok: float = pa.Field(nullable=True, coerce=True)
    varosok_del_alfold: float = pa.Field(nullable=True, coerce=True)
    varosok_del_dunantul: float = pa.Field(nullable=True, coerce=True)
    varosok_eszak_alfold: float = pa.Field(nullable=True, coerce=True)
    varosok_eszak_magyarorszag: float = pa.Field(nullable=True, coerce=True)
    varosok_kozep_dunantul: float = pa.Field(nullable=True, coerce=True)
    varosok_pest: float = pa.Field(nullable=True, coerce=True)
    varosok_nyugat_dunantul: float = pa.Field(nullable=True, coerce=True)
    kozsegek: float = pa.Field(nullable=True, coerce=True)

    class Config:
        coerce = True  # Automatikusan pd.to_datetime és numerikus konverziót futtat
        strict = True  # Nem enged meg extra, definiálatlan oszlopokat a DataFrame-ben


MnbDataFrame = pa.typing.DataFrame[MnbLakasarindexSchema]
m = MnbLakasarindexSchema
