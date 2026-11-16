"""Zero-R et GaussianNB : sélection temporelle reproductible et sorties séparées."""
import argparse
import hashlib
import platform
import subprocess
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
from sklearn.model_selection import GridSearchCV, cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from src.siad03_nb.contract import load_inputs
from src.siad03_extensions.data import ROOT, new_output, write_json
from src.siad03_extensions.evaluation import metrics, grouped_errors, calibration

# Grille fixée avant calcul : inclut les sept réglages du notebook et prolonge
# sa borne gagnante 0.01 ; aucun choix n'est effectué sur les scores 2024.
SMOOTHING = [10.0 ** exponent for exponent in range(-12, 2)]
SCORING = {'accuracy': 'accuracy', 'roc_auc': 'roc_auc',
           'average_precision': 'average_precision',
           'f1': make_scorer(f1_score, zero_division=0),
           'precision': make_scorer(precision_score, zero_division=0),
           'recall': make_scorer(recall_score, zero_division=0)}


def nb_pipeline():
    return Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
                     ('scaler', StandardScaler()), ('model', GaussianNB())])


def fit_models(train, features, folds, smoothing=None):
    """Aucune validation externe n'est acceptée par l'interface de sélection."""
    zero = Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
                     ('model', DummyClassifier(strategy='most_frequent'))])
    X, y = train[features], train.label
    baseline = cross_validate(zero, X, y, cv=folds, scoring=SCORING,
                              n_jobs=1, error_score='raise')
    zero.fit(X, y)
    search = GridSearchCV(nb_pipeline(), {'model__var_smoothing':
        SMOOTHING if smoothing is None else smoothing}, cv=folds, scoring=SCORING,
        refit='f1', n_jobs=1, error_score='raise', return_train_score=True)
    search.fit(X, y)
    return {'Zero-R': zero, 'GaussianNB': search.best_estimator_}, search, baseline


def run(output, data=None, protocol=None):
    train, val, features, folds, provenance = load_inputs(data, protocol)
    out = new_output(output)
    start = time.perf_counter()
    with threadpool_limits(limits=2):
        models, search, baseline = fit_models(train, features, folds)
    cv = pd.DataFrame(search.cv_results_)
    cv.to_csv(out / 'search.csv', index=False)
    fold_rows = []
    for i, (fit, check) in enumerate(folds):
        fold_rows.append(dict(year=int(train.iloc[check].year.min()),
            n_train=len(fit), n_validation=len(check),
            train_end=str(train.iloc[fit].date.max()), validation_start=str(train.iloc[check].date.min()),
            zeror_f1=baseline['test_f1'][i],
            nb_f1=cv.iloc[search.best_index_][f'split{i}_test_f1']))
    pd.DataFrame(fold_rows).to_csv(out / 'folds.csv', index=False)
    predictions = val[['cell_id', 'date', 'year', 'label']].copy()
    errors = val.assign(month=val.date.dt.month)
    rows = []
    for name, model in models.items():
        scores = model.predict_proba(val[features])[:, list(model.classes_).index(1)]
        predictions[name] = scores
        row = dict(model=name, **metrics(val.label, scores))
        for metric in SCORING:
            values = (baseline['test_' + metric] if name == 'Zero-R' else
                      [cv.iloc[search.best_index_][f'split{i}_test_{metric}'] for i in range(len(folds))])
            row['cv_' + metric + '_mean'] = float(np.mean(values))
            row['cv_' + metric + '_std'] = float(np.std(values))
        rows.append(row)
        path = out / (name + '.joblib')
        joblib.dump(model, path)
        np.testing.assert_allclose(joblib.load(path).predict_proba(val[features]),
                                   model.predict_proba(val[features]), rtol=0, atol=0)
        grouped_errors(errors, scores, 'month').to_csv(out / f'{name}_errors_month.csv', index=False)
        calibration(val.label, scores).to_csv(out / f'{name}_calibration.csv', index=False)
    predictions.to_csv(out / 'predictions_2024.csv', index=False)
    pd.DataFrame(rows).to_csv(out / 'metrics.csv', index=False)
    write_json(out / 'provenance.json', {**provenance, 'features': features,
        'base_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in Path(__file__).parent.glob('*.py')},
        'python': platform.python_version(), 'sklearn': sklearn.__version__,
        'numpy': np.__version__, 'pandas': pd.__version__,
        'grid': SMOOTHING, 'best_params': search.best_params_,
        'best_cv_f1': search.best_score_, 'selected_at_boundary':
            search.best_params_['model__var_smoothing'] in (SMOOTHING[0], SMOOTHING[-1]),
        'selection': 'F1 moyen des cinq plis train, seuil fixe 0.5 ; validation 2024 après sélection',
        'seconds': time.perf_counter() - start, 'test_evaluated': False})
    print(pd.DataFrame(rows)[['model', 'cv_f1_mean', 'f1', 'average_precision', 'roc_auc']].to_string(index=False))
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Dossier neuf, jamais écrasé')
    args = parser.parse_args()
    run(args.output)
