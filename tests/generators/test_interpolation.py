import pandas as pd
import pytest

from generators.interpolation import linear_interpolation
from models.ksh import KshIngatlanAdatSchema, TelepulesTipus, c


@pytest.fixture
def base_row_data():
    """Alapértelmezett érvényes adatsor sablon a Pandera sémához."""
    return {
        c.megye: "Pest",
        c.megye_slug: "pest",
        c.telaz: "12345",
        c.telepules_slug: "erd",
        c.tipus: TelepulesTipus.VAROS.value,
        c.szint: 2,
        c.kozter: "együtt",
        c.kozter_slug: "egyutt",
        c.ev: 2026,
        c.datum: pd.Timestamp("2026-01-01"),
        c.cshaz_ar: 500,
        c.tobbl_ar: 400,
        c.panel_ar: 300,
        c.total_ar: 400,
    }


def test_linear_interpolation_empty_dataframe():
    """Ha az input üres, egy érvényes, de üres DataFrame-et kell visszaadnia."""
    empty_df = KshIngatlanAdatSchema.validate(
        pd.DataFrame(columns=[col for col in c.__annotations__])
    )

    result = linear_interpolation(empty_df)

    assert result.empty
    assert list(result.columns) == list(empty_df.columns)


def test_linear_interpolation_megye_level(base_row_data: dict):
    """Megye szintű (szint=1) lineáris interpoláció és kerekítés tesztelése."""
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-01"),
            c.total_ar: 100,
        }
    )

    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-04"),
            c.total_ar: 103,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))

    result = linear_interpolation(df)

    assert len(result) == 4

    expected_dates = pd.Series(
        [
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-01-02"),
            pd.Timestamp("2026-01-03"),
            pd.Timestamp("2026-01-04"),
        ],
        name=c.datum,
    ).astype(result[c.datum].dtype)

    pd.testing.assert_series_equal(
        result[c.datum].reset_index(drop=True), expected_dates
    )

    assert result.loc[result[c.datum] == "2026-01-02", c.total_ar].values[0] == 101
    assert result.loc[result[c.datum] == "2026-01-03", c.total_ar].values[0] == 102


def test_linear_interpolation_telepules_level(base_row_data: dict):
    """Település szintű (szint!=1 és kozter=='együtt') interpoláció és csoportosítás tesztelése."""
    row1_g1 = base_row_data.copy()
    row1_g1.update(
        {
            c.megye_slug: "pest",
            c.telepules_slug: "erd",
            c.datum: pd.Timestamp("2026-01-01"),
            c.total_ar: 100,
        }
    )
    row2_g1 = base_row_data.copy()
    row2_g1.update(
        {
            c.megye_slug: "pest",
            c.telepules_slug: "erd",
            c.datum: pd.Timestamp("2026-01-03"),
            c.total_ar: 200,
        }
    )

    row1_g2 = base_row_data.copy()
    row1_g2.update(
        {
            c.megye_slug: "pest",
            c.telepules_slug: "budaors",
            c.datum: pd.Timestamp("2026-01-01"),
            c.total_ar: 500,
        }
    )
    row2_g2 = base_row_data.copy()
    row2_g2.update(
        {
            c.megye_slug: "pest",
            c.telepules_slug: "budaors",
            c.datum: pd.Timestamp("2026-01-03"),
            c.total_ar: 600,
        }
    )

    df = KshIngatlanAdatSchema.validate(
        pd.DataFrame([row1_g1, row2_g1, row1_g2, row2_g2])
    )

    result = linear_interpolation(df)

    assert len(result) == 6

    erd_jan2 = result[
        (result[c.telepules_slug] == "erd") & (result[c.datum] == "2026-01-02")
    ]
    assert erd_jan2[c.total_ar].values[0] == 150

    budaors_jan2 = result[
        (result[c.telepules_slug] == "budaors") & (result[c.datum] == "2026-01-02")
    ]
    assert budaors_jan2[c.total_ar].values[0] == 550


def test_linear_interpolation_utca_level(base_row_data: dict):
    """Utca szintű (szint!=1, kozter nem null és nem 'együtt') tesztelése."""
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 3,
            c.kozter: "Almafa utca",
            c.kozter_slug: "almafa-utca",
            c.datum: pd.Timestamp("2026-01-01"),
            c.total_ar: 10,
        }
    )
    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 3,
            c.kozter: "Almafa utca",
            c.kozter_slug: "almafa-utca",
            c.datum: pd.Timestamp("2026-01-03"),
            c.total_ar: 30,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))

    result = linear_interpolation(df)

    assert len(result) == 3
    utca_jan2 = result[
        (result[c.kozter_slug] == "almafa-utca") & (result[c.datum] == "2026-01-02")
    ]
    assert utca_jan2[c.total_ar].values[0] == 20


def test_non_numeric_cols_ffill_and_bfill(base_row_data: dict):
    """Ellenőrzi, hogy a nem-numerikus oszlopok helyesen töltődnek-e fel ffill/bfill segítségével."""
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-01"),
            c.megye: "Pest",
            c.total_ar: 100,
        }
    )
    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-03"),
            c.megye: "Pest",
            c.total_ar: 200,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))

    result = linear_interpolation(df)

    jan2_row = result[result[c.datum] == "2026-01-02"].iloc[0]
    assert jan2_row[c.megye] == "Pest"
    assert jan2_row[c.telaz] == "12345"
    assert jan2_row[c.tipus] == TelepulesTipus.VAROS.value


def test_linear_interpolation_rounding_and_int_conversion(base_row_data: dict):
    """Ellenőrzi, hogy a lebegőpontos interpolált árakat megfelelően kerekíti és Int64 típusra kényszeríti."""
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-01"),
            c.total_ar: 100,
        }
    )
    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-04"),
            c.total_ar: 105,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))

    result = linear_interpolation(df)

    assert result.loc[result[c.datum] == "2026-01-02", c.total_ar].values[0] == 102
    assert result.loc[result[c.datum] == "2026-01-03", c.total_ar].values[0] == 103


def test_linear_interpolation_limit_direction_both(base_row_data: dict):
    """Ellenőrzi a limit_direction='both' működését egy nullable ároszlopon (cshaz_ar),
    ha hiányzó érték van a csoport szélén.
    """
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-01"),
            c.cshaz_ar: None,
            c.total_ar: 100,
        }
    )

    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-01-02"),
            c.cshaz_ar: 200,
            c.total_ar: 100,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))

    result = linear_interpolation(df)

    jan1_cshaz = result.loc[result[c.datum] == "2026-01-01", c.cshaz_ar].values[0]

    assert jan1_cshaz == 200


def test_linear_interpolation_does_not_extend_beyond_bounds(base_row_data: dict):
    """Ellenőrzi, hogy az interpoláció szigorúan csak a legelső és legutolsó dátum között fut,
    és nem generál adatot a határokon kívülre.
    """
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-06-10"),
            c.total_ar: 100,
        }
    )
    row2 = base_row_data.copy()
    row2.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-06-12"),
            c.total_ar: 102,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1, row2]))
    result = linear_interpolation(df)

    actual_dates = result[c.datum].dt.strftime("%Y-%m-%d").tolist()
    assert actual_dates == ["2026-06-10", "2026-06-11", "2026-06-12"]


def test_linear_interpolation_single_day_group(base_row_data: dict):
    """Ha egy csoportban csak egyetlen nap szerepel, az interpolációnak nem szabad
    új napokat generálnia, a meglévő sort kell visszaadnia.
    """
    row1 = base_row_data.copy()
    row1.update(
        {
            c.szint: 1,
            c.kozter: None,
            c.kozter_slug: None,
            c.datum: pd.Timestamp("2026-06-20"),
            c.total_ar: 500,
        }
    )

    df = KshIngatlanAdatSchema.validate(pd.DataFrame([row1]))
    result = linear_interpolation(df)

    actual_dates = result[c.datum].dt.strftime("%Y-%m-%d").tolist()
    assert actual_dates == ["2026-06-20"]
    assert result.iloc[0][c.total_ar] == 500
