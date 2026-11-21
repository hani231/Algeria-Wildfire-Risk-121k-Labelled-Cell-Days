"""Modèles obligatoires et recherche chronologique du benchmark collectif."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

from src.siad03_extensions.data import ROOT, new_output, write_json
from src.siad03_extensions.evaluation import metrics
from src.siad03_nb.contract import load_inputs
from src.siad03_nb.experiment import SMOOTHING

CONFIG = ROOT/'config/protocole.json'
LOT = ROOT/'results/benchmark_final'
MANDATORY = ('Zero-R', 'GaussianNB', 'DecisionTree', 'Random Forest', 'K-NN', 'SVM')


def candidates(name, seed):
    # Configurations contrastées fixées avant lecture de la validation externe.
    specs = {
        'Zero-R': (DummyClassifier(strategy='most_frequent'), [{}]),
        'GaussianNB': (GaussianNB(), [{'var_smoothing': SMOOTHING}]),
        'DecisionTree': (DecisionTreeClassifier(random_state=seed), [
            {'criterion': [criterion], 'max_depth': [depth], 'min_samples_leaf': [leaf],
             'ccp_alpha': [alpha], 'class_weight': ['balanced']}
            for criterion in ['gini', 'entropy'] for depth, leaf, alpha in [(5, 30, 0), (10, 80, .0002)]]),
        'Random Forest': (RandomForestClassifier(random_state=seed, n_jobs=1), [
            {'n_estimators': [n], 'max_depth': [d], 'min_samples_leaf': [k],
             'max_features': [m], 'class_weight': [w]}
            for n,d,k,m,w in [(24,7,30,'sqrt',None),(32,10,50,.4,'balanced'),(24,7,30,'sqrt','balanced')]]),
        'K-NN': (KNeighborsClassifier(algorithm='brute'), [
            {'n_neighbors':[k], 'p':[p], 'weights':[w]}
            for k,p,w in [(15,1,'uniform'),(15,2,'uniform'),(45,2,'distance'),(45,1,'distance')]]),
        'SVM': (SVC(probability=True, random_state=seed, class_weight='balanced'), [
            {'kernel':['linear'], 'C':[.1,1]}, {'kernel':['rbf'], 'C':[.5,2], 'gamma':['scale']},
            {'kernel':['poly'], 'degree':[2], 'C':[1], 'gamma':['scale', .1]}]),
    }
    model, grid = specs[name]
    steps = [SimpleImputer(strategy='median', keep_empty_features=True)]
    if name in ('SVM','GaussianNB','K-NN'):
        steps.append(StandardScaler())
    pipe = make_pipeline(*steps, model)
    prefix = pipe.steps[-1][0] + '__'
    return pipe, [{prefix+k:v for k,v in candidate.items()} for candidate in grid]


def limited(indices, y, cap, seed):
    if cap is None or len(indices) <= cap:
        return indices
    chosen, _ = train_test_split(indices, train_size=cap, stratify=y.iloc[indices], random_state=seed)
    return np.sort(chosen)


def positive_f1(model, X, y):
    return f1_score(y, model.predict_proba(X)[:,1] >= .5, zero_division=0)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    cfg = json.loads(CONFIG.read_text())
    train, val, features, folds, provenance = load_inputs(protocol=CONFIG)
    raw_hash = provenance['raw_sha256']
    if raw_hash != cfg['raw_sha256']:
        raise ValueError('Empreinte du dataset incompatible avec ce protocole.')
    out = new_output(output)
    scores = val[['date','cell_id','year','label']].copy()
    rows, manifest = [], {}
    y = train.label
    for name in MANDATORY:
        print('Recherche', name, flush=True)
        estimator, grid = candidates(name, cfg['seed'])
        cap = cfg['train_caps'].get(name)
        splits = [(limited(fit, y, cap, cfg['seed']), check) for fit,check in folds]
        search = GridSearchCV(estimator, grid, scoring=positive_f1, cv=splits,
                              n_jobs=2, refit=False, error_score='raise')
        X = train[features]
        start = perf_counter()
        search.fit(X, y)
        search_seconds = perf_counter()-start
        pd.DataFrame(search.cv_results_).to_csv(out/f'{name}_cv.csv', index=False)
        ix = limited(np.arange(len(y)), y, cap, cfg['seed'])
        model = clone(estimator).set_params(**search.best_params_)
        start = perf_counter()
        model.fit(X.iloc[ix], y.iloc[ix])
        fit_seconds = perf_counter()-start
        path = out/f'{name}.joblib'
        joblib.dump(model, path, compress=3)
        start = perf_counter()
        pred = model.predict_proba(val[features])[:,1]
        predict_seconds = perf_counter()-start
        np.testing.assert_allclose(pred, joblib.load(path).predict_proba(val[features])[:,1], atol=0, rtol=0)
        scores[name] = pred
        rows.append(dict(model=name, **metrics(val.label, pred), cv_f1=search.best_score_,
                         fit_seconds=fit_seconds, predict_seconds=predict_seconds, search_seconds=search_seconds))
        manifest[name] = dict(params=search.best_params_, n_fit=len(ix), sha256=digest(path),
                              fold_fit=[len(fit) for fit,_ in splits], fold_check=[len(v) for _,v in splits])
    scores.to_csv(out/'predictions_validation.csv', index=False)
    pd.DataFrame(rows).to_csv(out/'metrics.csv', index=False)
    write_json(out/'manifest.json', dict(models=manifest, raw_sha256=raw_hash,
               config_sha256=digest(CONFIG), python=platform.python_version(), sklearn=sklearn.__version__,
               numpy=np.__version__, pandas=pd.__version__, joblib=joblib.__version__))
    trials = [dict(model=n, threshold=t, f1=metrics(val.label, scores[n], t)['f1'])
              for n in MANDATORY for t in cfg['thresholds']]
    ranking = pd.DataFrame(trials).sort_values(['f1','threshold','model'],ascending=[False,False,True])
    ranking.to_csv(out/'thresholds_2024.csv',index=False)
    best = ranking.iloc[0].to_dict()
    write_json(out/'decision.json', {**best, 'refit':False, 'sha256':manifest[best['model']]['sha256'],
                                     'config_sha256':digest(CONFIG), 'raw_sha256':raw_hash})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
