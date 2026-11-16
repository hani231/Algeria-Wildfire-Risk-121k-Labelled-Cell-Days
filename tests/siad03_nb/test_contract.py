import json
import pytest
from pandas.testing import assert_frame_equal
from src.siad03_nb.contract import load_inputs, validate_protocol
from src.siad03_extensions.data import ROOT


def config():
    return json.loads((ROOT / 'results/protocole_propose.json').read_text())


@pytest.mark.parametrize('column', ['label', 'split', 'date', 'year', 'cell_id',
    'sample_kind', 'n_detections', 'max_frp', 'days_since_last_fire', 'ndvi_normal', 'ndvi_anomaly'])
def test_reject_leakage(column):
    c = config(); c['features'].append(column)
    with pytest.raises(ValueError, match='Prédicteurs'):
        validate_protocol(c)


@pytest.mark.parametrize('key,value', [('train', '2012-2024'), ('validation', '2025'),
    ('test_reserve', '2024'), ('metrique_principale', 'accuracy'),
    ('cv_annees_validation', [2020, 2021, 2022, 2023, 2024])])
def test_reject_changed_contract(key, value):
    c = config(); c[key] = value
    with pytest.raises(ValueError, match=key):
        validate_protocol(c)


def test_real_folds_and_no_heldout_influence(monkeypatch):
    import pandas as pd
    from src.siad03_extensions import data
    before = load_inputs()
    raw = pd.read_csv(ROOT / 'Dataset/dataset.csv')
    raw.loc[raw.split.eq('test'), ['temp_max', 'label']] = -999
    monkeypatch.setattr(data.pd, 'read_csv', lambda *a, **k: raw.copy())
    after = load_inputs()
    for a, b in zip(before[:2], after[:2]):
        assert_frame_equal(a, b)
    train, val, features, folds, _ = after
    assert set(val.year) == {2024}
    assert len(folds) == 5
    for year, (fit, check) in zip(range(2019, 2024), folds):
        assert train.iloc[fit].date.max() < train.iloc[check].date.min()
        assert set(train.iloc[check].year) == {year}
