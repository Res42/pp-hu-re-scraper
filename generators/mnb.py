from models.ksh import IngatlanDataFrame, TelepulesTipus
from models.mnb import MnbDataFrame, m

MEGYE_REGIO_MAP = {
    "13": m.varosok_pest,  # Pest
    "07": m.varosok_kozep_dunantul,  # Fejér
    "11": m.varosok_kozep_dunantul,  # Komárom-Esztergom
    "19": m.varosok_kozep_dunantul,  # Veszprém
    "08": m.varosok_nyugat_dunantul,  # Győr-Moson-Sopron
    "18": m.varosok_nyugat_dunantul,  # Vas
    "20": m.varosok_nyugat_dunantul,  # Zala
    "02": m.varosok_del_dunantul,  # Baranya
    "14": m.varosok_del_dunantul,  # Somogy
    "17": m.varosok_del_dunantul,  # Tolna
    "05": m.varosok_eszak_magyarorszag,  # Borsod-Abaúj-Zemplén
    "10": m.varosok_eszak_magyarorszag,  # Heves
    "12": m.varosok_eszak_magyarorszag,  # Nógrád
    "09": m.varosok_eszak_alfold,  # Hajdú-Bihar
    "15": m.varosok_eszak_alfold,  # Szabolcs-Szatmár-Bereg
    "16": m.varosok_eszak_alfold,  # Jász-Nagykun-Szolnok
    "03": m.varosok_del_alfold,  # Bács-Kiskun
    "04": m.varosok_del_alfold,  # Békés
    "06": m.varosok_del_alfold,  # Csongrád-Csanád
}


def get_mnb_column_for_ksh_row(megye: str, tipus: TelepulesTipus) -> str:
    if (
        tipus in [TelepulesTipus.BUDAPEST, TelepulesTipus.BUDAPEST_KERULET]
        or megye == "01"
    ):
        return m.budapest

    if tipus == TelepulesTipus.KOZSEG:
        return m.kozsegek

    if megye in MEGYE_REGIO_MAP:
        return MEGYE_REGIO_MAP[megye]

    return m.varosok


def add_mnb_to_ksh(df_ksh: IngatlanDataFrame, df_mnb: MnbDataFrame):
    # TODO impl
    return df_ksh
