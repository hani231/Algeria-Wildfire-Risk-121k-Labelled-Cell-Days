"""Comparer quelques paramètres isolément sur les cinq plis de développement."""
import argparse
import json
from pathlib import Path
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV
from threadpoolctl import threadpool_limits
from src.models import LOT, candidates, limited, positive_f1
from src.preprocessing import development_inputs, read_protocol
from src.siad03_extensions.data import new_output

# Chaque famille conserve le réglage publié comme témoin.
VARIANTS = {
    'K-NN': [{'weights': 'distance'}, {'n_neighbors': 45}, {'p': 1}],
    'DecisionTree': [{'criterion': 'entropy'}, {'ccp_alpha': 0}, {'min_samples_leaf': 30}],
    'Random Forest': [{'class_weight': None}, {'max_depth': 7}, {'n_estimators': 48}],
    'SVM': [{'kernel': 'rbf'}, {'kernel': 'rbf', 'gamma': 0.1}],
}


def run(output):
    train, _, features, folds, _ = development_inputs()
    config = read_protocol()
    manifest = json.loads((LOT/'manifest.json').read_text())['models']
    folder = new_output(output)
    for name, variants in VARIANTS.items():
        pipe, _ = candidates(name, config['seed'])
        pipe.set_params(**manifest[name]['params'])
        prefix = pipe.steps[-1][0] + '__'
        grid = [{prefix+k: [v] for k, v in variant.items()} for variant in [{}, *variants]]
        splits = [(limited(fit, train.label, config['train_caps'].get(name), config['seed']), check)
                  for fit, check in folds]
        search = GridSearchCV(clone(pipe), grid, cv=splits, scoring=positive_f1,
                              refit=False, n_jobs=1, error_score='raise')
        search.fit(train[features], train.label)
        pd.DataFrame(search.cv_results_).to_csv(folder/f'{name}.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
