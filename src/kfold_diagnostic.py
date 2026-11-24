"""Expérience complémentaire sur 2012–2023. Aucune sauvegarde de modèle."""
import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GridSearchCV, KFold
from threadpoolctl import threadpool_limits

from src.models import LOT, MANDATORY, candidates, limited, positive_f1
from src.preprocessing import development_inputs, read_protocol
from src.siad03_extensions.data import new_output


def diagnostic_folds(train, cap, seed):
    if not train.split.eq('train').all() or not train.year.between(2012, 2023).all():
        raise ValueError('Le diagnostic exige exclusivement le train 2012–2023.')
    splitter = KFold(n_splits=5, shuffle=True, random_state=seed)
    return [(limited(fit, train.label, cap, seed), check) for fit, check in splitter.split(train)]


def run(folder):
    train, _, features, _, _ = development_inputs()
    config = read_protocol()
    manifest = json.loads((LOT/'manifest.json').read_text())['models']
    output = new_output(folder)
    summary = []
    for name in MANDATORY:
        estimator, grid = candidates(name, config['seed'])
        folds = diagnostic_folds(train, config['train_caps'].get(name), config['seed'])
        search = GridSearchCV(estimator, grid, scoring=positive_f1, cv=folds,
                              refit=False, return_train_score=True, n_jobs=2, error_score='raise')
        search.fit(train[features], train.label)
        results = pd.DataFrame(search.cv_results_)
        results.to_csv(output/f'{name}.csv', index=False)
        # Compare each protocol at the already-frozen parameters, independent of the new ranking.
        row = results[results.params.map(lambda params: params == manifest[name]['params'])].iloc[0]
        for i, (fit, check) in enumerate(folds):
            summary.append(dict(model=name, fold=i+1, n_fit=len(fit), n_check=len(check),
                                first_check_year=int(train.year.iloc[check].min()),
                                last_fit_year=int(train.year.iloc[fit].max()),
                                f1_fit=row[f'split{i}_train_score'], f1_check=row[f'split{i}_test_score']))
        print(name, flush=True)
    pd.DataFrame(summary).to_csv(output/'folds.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
