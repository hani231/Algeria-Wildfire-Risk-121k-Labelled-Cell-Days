import hashlib
import json
import joblib
import numpy as np
import pandas as pd
import pytest
from src.siad03_nb.contract import load_inputs
from src.siad03_extensions.data import ROOT, new_output
from src.siad03_extensions.evaluation import metrics


def test_executed_artifacts_match_predictions_and_selection():
    out = ROOT / 'results/siad03_nb/run_01'
    train, val, features, folds, _ = load_inputs()
    pred = pd.read_csv(out / 'predictions_2024.csv')
    np.testing.assert_array_equal(pred.label, val.label)
    np.testing.assert_array_equal(pred.cell_id, val.cell_id)
    assert pd.to_datetime(pred.date).equals(val.date)
    scores = pd.read_csv(out / 'metrics.csv').set_index('model')
    for name in scores.index:
        model = joblib.load(out / f'{name}.joblib')
        np.testing.assert_allclose(model.predict_proba(val[features])[:, 1], pred[name], atol=1e-15)
        for key, value in metrics(val.label, pred[name]).items():
            assert np.isclose(value, scores.loc[name, key])
        errors = pd.read_csv(out / f'{name}_errors_month.csv')
        for key in ['n','tp','fp','tn','fn']:
            assert errors[key].sum() == scores.loc[name, key]
    cv = pd.read_csv(out / 'search.csv')
    meta = json.loads((out / 'provenance.json').read_text())
    assert len(cv) == 14
    assert len(folds) == 5
    assert np.isclose(cv.mean_test_f1.max(), meta['best_cv_f1'])
    assert np.isclose(cv.loc[cv.mean_test_f1.idxmax(), 'param_model__var_smoothing'],
                      meta['best_params']['model__var_smoothing'])
    assert not meta['test_evaluated']
    for name, sha in meta['source_sha256'].items():
        assert hashlib.sha256((ROOT / 'src/siad03_nb' / name).read_bytes()).hexdigest() == sha
    # Reproduce the historical seven configurations instead of claiming a new baseline.
    old = pd.read_csv(ROOT / 'results/recherche_naive_bayes.csv')
    for row in old.itertuples():
        match = cv.loc[np.isclose(cv.param_model__var_smoothing,
                                 row.param_model__var_smoothing, rtol=1e-10, atol=0)]
        assert len(match) == 1
        assert np.isclose(match.iloc[0].mean_test_f1, row.mean_test_f1)


def test_no_output_overwrite(tmp_path):
    folder = new_output(tmp_path / 'run')
    marker = folder / 'result.txt'; marker.write_text('preserve')
    with pytest.raises(FileExistsError):
        new_output(folder)
    assert marker.read_text() == 'preserve'


def test_diagnostic_figures(tmp_path):
    from src.siad03_nb.diagnostics import run
    out = run(ROOT / 'results/siad03_nb/run_01', tmp_path / 'figures')
    assert {p.name for p in out.iterdir()} == {'search.png', 'curves.png', 'confusion.png'}
    assert all(p.stat().st_size > 1000 for p in out.iterdir())
