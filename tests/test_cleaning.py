import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.cleaning_guide import clean_data, LEAKAGE_COLUMNS


def test_cleaning_is_non_mutating_idempotent_and_preserves_missing(small_data):
    original = small_data.copy(deep=True)
    clean, report = clean_data(small_data)
    assert_frame_equal(small_data, original)
    assert_frame_equal(clean_data(clean)[0], clean)
    assert not set(LEAKAGE_COLUMNS).intersection(clean.columns)
    assert clean.ndvi.isna().all()
    assert clean.days_since_last_fire.eq(9999).all()
    assert not any(report['controles_coherence'].values())


@pytest.mark.parametrize('column,value', [
    ('rh_mean', 101), ('rh_min', -1), ('temp_mean', 40),
    ('wind_max', -1), ('wind_mean', 4), ('precip_sum', -1),
    ('ndvi', 2), ('temp_max', np.inf), ('label', 2),
    ('date', 'date inconnue'), ('split', 'inconnu'), ('year', 2023),
    ('doy', 1), ('cell_id', ''), ('temp_mean', 'inconnu'),
])
def test_invalid_input_is_rejected(small_data, column, value):
    bad = small_data.copy()
    if isinstance(value, str):
        bad[column] = bad[column].astype(object)
    bad.loc[0, column] = value
    with pytest.raises(ValueError):
        clean_data(bad)


def test_missing_schema_has_clear_error(small_data):
    with pytest.raises(ValueError, match='label'):
        clean_data(small_data.drop(columns='label'))


def test_duplicate_exact_removed_conflict_rejected(small_data):
    doubled = pd.concat([small_data, small_data.iloc[[0]]], ignore_index=True)
    clean, report = clean_data(doubled)
    assert len(clean) == len(small_data)
    assert report['doublons_exacts_supprimes'] == 1
    doubled.loc[len(doubled) - 1, 'temp_max'] = 35
    with pytest.raises(ValueError, match='même clé'):
        clean_data(doubled)


def test_export_index_only_removed_if_verified(small_data):
    with_index = small_data.assign(**{'Unnamed: 0': np.arange(len(small_data))})
    assert 'Unnamed: 0' not in clean_data(with_index)[0]
    with_index.loc[0, 'Unnamed: 0'] = 50
    with pytest.raises(ValueError, match='index'):
        clean_data(with_index)


def test_duplicate_trimmed_names_and_empty_rejected(small_data):
    bad = small_data.assign(**{' label ': 1})
    with pytest.raises(ValueError, match='répétés'):
        clean_data(bad)
    with pytest.raises(ValueError, match='aucune observation'):
        clean_data(small_data.iloc[:0])
