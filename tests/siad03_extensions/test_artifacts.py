"""Tests d'intégration des résultats réellement produits (pas de réentraînement)."""
import json
import joblib
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from src.siad03_extensions.data import ROOT, load_development
from src.siad03_extensions.evaluation import metrics


def test_predictions_and_existing_metrics_are_reproduced():
    folder = ROOT/'results/siad03_extensions/benchmark'
    pred = pd.read_csv(folder/'predictions_validation.csv', parse_dates=['date'])
    train, val, features, _ = load_development()
    assert_frame_equal(pred[['cell_id','date','label']], val[['cell_id','date','label']], check_dtype=False)
    scores = pd.read_csv(folder/'metrics.csv').set_index('model')
    old = pd.concat([pd.read_csv(ROOT/'results/resultats_zeror_nb_validation.csv'),
                    pd.read_csv(ROOT/'results/resultats_arbre_decision_validation.csv')]).set_index('model')
    for name in scores.index:
        got = metrics(pred.label, pred[name])
        for key in ['f1','roc_auc','average_precision','brier','tn','fp','fn','tp']:
            assert np.isclose(got[key], scores.loc[name,key])
        if name in old.index:
            for key in ['f1','roc_auc','average_precision']:
                assert np.isclose(got[key], old.loc[name,'val2024_'+key])
        else:
            model = joblib.load(folder/f'{name}.joblib')
            np.testing.assert_allclose(model.predict_proba(val[features])[:,1],pred[name])
        for group in ['month','season','spatial_block','temp_max_bin','rh_mean_bin','precip_sum_bin','seen_cell']:
            errors = pd.read_csv(folder/f'{name}_errors_{group}.csv')
            assert errors.n.sum() == len(val)
            for key in ['tn','fp','fn','tp']: assert errors[key].sum() == got[key]
    summary = json.loads((folder/'search_summary.json').read_text())
    for name in summary:
        cv = pd.read_csv(folder/f'{name}_cv.csv')
        assert len(cv) == summary[name]['candidates']
        assert len([c for c in cv if c.startswith('split') and c.endswith('_test_f1')]) == 5
        assert np.isclose(cv.mean_test_f1.max(),summary[name]['cv_f1'])


def test_statistics_reproduced_and_test_values_unused(monkeypatch):
    from src.siad03_extensions import data
    raw = pd.read_csv(ROOT/'Dataset/dataset.csv')
    expected = load_development()[:2]
    raw.loc[raw.split.eq('test'), ['label','temp_max']] = -999
    monkeypatch.setattr(data.pd, 'read_csv', lambda *a, **k: raw.copy())
    actual = load_development()[:2]
    for a,b in zip(expected,actual): assert_frame_equal(a,b)
