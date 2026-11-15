"""Benchmark indépendant : régression logistique et HistGradientBoosting."""
import argparse
import platform
import time
import warnings
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from threadpoolctl import threadpool_limits
from src.train_decision_tree import build_temporal_splits
from src.siad03_extensions.data import ROOT, load_development, new_output, write_json
from src.siad03_extensions.evaluation import metrics, calibration, grouped_errors, cluster_intervals


def candidates():
    return {
        'LogisticRegression': (make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
            LogisticRegression(max_iter=1500, random_state=42)),
            {'logisticregression__C': [.01, 1, 100],
             'logisticregression__class_weight': [None, 'balanced']}),
        # Pas d'arrêt précoce avec partition aléatoire interne au train temporel.
        'HistGradientBoosting': (HistGradientBoostingClassifier(random_state=42,
            early_stopping=False, max_iter=100, learning_rate=.1),
            {'max_leaf_nodes': [7, 15], 'l2_regularization': [0, 10],
             'class_weight': [None, 'balanced']})}


def run(output):
    out = new_output(output)
    train, val, features, provenance = load_development()
    folds = build_temporal_splits(train, [2019, 2020, 2021, 2022, 2023])
    records, searches, fitted = [], {}, {}
    write_json(out / 'provenance.json', {**provenance, 'features': features,
        'python': platform.python_version(), 'sklearn': sklearn.__version__,
        'selection': 'mean F1 over 5 expanding chronological folds; threshold=0.5',
        'protocol_status': 'proposition_a_harmoniser', 'random_state': 42})
    pd.DataFrame([dict(validation_year=int(train.iloc[v].year.min()),
        n_train=len(t), n_validation=len(v), train_end=str(train.iloc[t].date.max()),
        val_start=str(train.iloc[v].date.min())) for t, v in folds]).to_csv(out / 'folds.csv', index=False)
    for name, (estimator, grid) in candidates().items():
        start = time.perf_counter()
        search = GridSearchCV(estimator, grid, cv=folds,
            scoring={'f1': 'f1', 'average_precision': 'average_precision', 'roc_auc': 'roc_auc'},
            refit='f1', n_jobs=1, error_score='raise', return_train_score=True)
        search.fit(train[features], train.label)
        elapsed = time.perf_counter() - start
        model = search.best_estimator_
        joblib.dump(model, out / f'{name}.joblib')
        np.testing.assert_allclose(model.predict_proba(val[features]),
            joblib.load(out / f'{name}.joblib').predict_proba(val[features]))
        pd.DataFrame(search.cv_results_).to_csv(out / f'{name}_cv.csv', index=False)
        searches[name] = dict(best_params=search.best_params_, cv_f1=search.best_score_,
            seconds=elapsed, candidates=len(search.cv_results_['params']))
        fitted[name] = model
        print(name, searches[name], flush=True)
    # Artefacts existants utilisés en lecture seule. Leurs avertissements restent visibles et archivés.
    existing = {'Zero-R': 'zeror_developpement.joblib', 'GaussianNB': 'naive_bayes_developpement.joblib',
                'DecisionTree': 'arbre_decision_developpement.joblib'}
    notices = {}
    for name, filename in existing.items():
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            fitted[name] = joblib.load(ROOT / 'models' / filename)
        notices[name] = [str(w.message) for w in ws]
    predictions = val[['cell_id', 'date', 'year', 'label', 'lat', 'lon', 'temp_max', 'rh_mean', 'precip_sum']].copy()
    val = val.copy(); val['month'] = val.date.dt.month
    val['season'] = val['month'].map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'})
    for col in ['temp_max', 'rh_mean', 'precip_sum']:
        # Bornes apprises exclusivement sur train, infinis pour conserver les extrêmes 2024.
        cuts = np.unique(train[col].quantile([.25, .5, .75]).to_numpy())
        val[col + '_bin'] = pd.cut(val[col], [-np.inf, *cuts, np.inf])
    val['spatial_block'] = np.floor(val.lat).astype(str) + ':' + np.floor(val.lon).astype(str)
    val['seen_cell'] = val.cell_id.isin(train.cell_id.unique())
    for name, model in fitted.items():
        start = time.perf_counter()
        score = model.predict_proba(val[features])[:, list(model.classes_).index(1)]
        predict_seconds = time.perf_counter() - start
        predictions[name] = score
        records.append(dict(model=name, **metrics(val.label, score), predict_seconds=predict_seconds))
        calibration(val.label, score).to_csv(out / f'{name}_calibration.csv', index=False)
        cluster_intervals(val.label, score, val.cell_id).to_csv(out / f'{name}_intervals.csv', index=False)
        for group in ['month', 'season', 'spatial_block', 'seen_cell', 'temp_max_bin', 'rh_mean_bin', 'precip_sum_bin']:
            grouped_errors(val, score, group).to_csv(out / f'{name}_errors_{group}.csv', index=False)
        pd.DataFrame([dict(threshold=t, **metrics(val.label, score, t)) for t in [.1,.2,.3,.4,.5,.6,.7,.8,.9]]).to_csv(out / f'{name}_threshold_sensitivity.csv', index=False)
    predictions.to_csv(out / 'predictions_validation.csv', index=False)
    pd.DataFrame(records).to_csv(out / 'metrics.csv', index=False)
    write_json(out / 'search_summary.json', searches)
    write_json(out / 'artifact_warnings.json', notices)
    print(pd.DataFrame(records)[['model', 'f1', 'average_precision', 'roc_auc', 'brier']].to_string(index=False), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='results/siad03_extensions/benchmark')
    args = parser.parse_args()
    with threadpool_limits(limits=2):
        run(args.output)
