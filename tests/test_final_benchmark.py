"""Relecture des preuves du benchmark publié, sans nouvel ajustement."""
import json
import joblib
import numpy as np
import pandas as pd
import pytest
from threadpoolctl import threadpool_limits

from src.models import CONFIG, LOT, MANDATORY, digest
from src.siad03_nb.contract import load_inputs
from src.siad03_extensions.data import ROOT
from src.siad03_extensions.evaluation import metrics


@pytest.fixture(scope='module')
def development():
    return load_inputs(protocol=CONFIG)


@pytest.mark.parametrize('name', MANDATORY)
def test_saved_validation_predictions(name, development):
    _, val, features, folds, _ = development
    manifest = json.loads((LOT/'manifest.json').read_text())
    record = manifest['models'][name]
    model_file = LOT/(name+'.joblib')
    assert digest(model_file) == record['sha256']
    assert len(record['fold_fit']) == len(folds) == 5
    assert not set(features).intersection({'date','cell_id','year','lat','lon','label','split',
                                          'n_detections','sample_kind','max_frp','days_since_last_fire',
                                          'ndvi_normal','ndvi_anomaly'})
    with threadpool_limits(limits=1):
        probs = joblib.load(model_file).predict_proba(val[features])[:,1]
    saved = pd.read_csv(LOT/'predictions_validation.csv')
    assert np.array_equal(saved.cell_id, val.cell_id)
    assert np.array_equal(pd.to_datetime(saved.date), val.date)
    np.testing.assert_allclose(saved[name], probs, atol=1e-12, rtol=1e-12)
    row = pd.read_csv(LOT/'metrics.csv').set_index('model').loc[name]
    for key, value in metrics(val.label, probs).items():
        assert row[key] == pytest.approx(value)


def test_final_score_matches_frozen_decision():
    frozen = json.loads((LOT/'decision.json').read_text())
    result = json.loads((ROOT/'results/test_final/result.json').read_text())
    predictions = pd.read_csv(ROOT/'results/test_final/predictions.csv')
    assert frozen['config_sha256'] == digest(CONFIG)
    assert result['model'] == frozen['model'] and result['threshold'] == frozen['threshold']
    assert predictions.year.eq(2025).all() and len(predictions) == 8467
    for key, value in metrics(predictions.label, predictions.score, frozen['threshold']).items():
        assert result[key] == pytest.approx(value)


@pytest.mark.parametrize('name', MANDATORY)
def test_frozen_parameters_match_search_and_serialized_pipeline(name, development):
    from ast import literal_eval
    from sklearn.model_selection import ParameterGrid
    from src.models import candidates, limited
    train, _, _, folds, _ = development
    config = json.loads(CONFIG.read_text())
    entry = json.loads((LOT/'manifest.json').read_text())['models'][name]
    cv = pd.read_csv(LOT/f'{name}_cv.csv')
    _, grid = candidates(name, config['seed'])
    assert list(cv.params.map(literal_eval)) == list(ParameterGrid(grid))
    fold_scores = cv[[f'split{i}_test_score' for i in range(5)]]
    np.testing.assert_allclose(fold_scores.mean(axis=1), cv.mean_test_score)
    winner = cv.iloc[fold_scores.mean(axis=1).argmax()]
    assert literal_eval(winner.params) == entry['params']
    params = joblib.load(LOT/(name+'.joblib')).get_params()
    assert all(params[key] == value for key, value in entry['params'].items())
    for i, (fit, check) in enumerate(folds):
        selected = limited(fit, train.label, config['train_caps'].get(name), config['seed'])
        assert (len(selected), len(check)) == (entry['fold_fit'][i], entry['fold_check'][i])
        assert train.year.iloc[selected].max() < train.year.iloc[check].min()
