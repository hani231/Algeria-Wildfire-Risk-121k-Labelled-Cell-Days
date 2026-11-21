"""Sensibilité au groupe de variables, sur les cinq années internes uniquement."""
import argparse
from pathlib import Path
import pandas as pd
from src.models import CONFIG, candidates
from src.siad03_nb.contract import load_inputs
from src.siad03_extensions.evaluation import metrics


def compare(path):
    train, _, features, folds, _ = load_inputs(protocol=CONFIG)
    groups = {'météo du jour': features[:9], 'météo et historique': features[:14],
              'ensemble des prédicteurs': features}
    rows = []
    for group, columns in groups.items():
        for fit, check in folds:
            model, _ = candidates('GaussianNB', 42)
            model.set_params(gaussiannb__var_smoothing=1.0)
            model.fit(train.iloc[fit][columns], train.label.iloc[fit])
            sample = train.iloc[check]
            scores = model.predict_proba(sample[columns])[:,1]
            rows.append(dict(groupe=group, dimensions=len(columns), annee=sample.year.min(),
                             **metrics(sample.label, scores)))
    pd.DataFrame(rows).to_csv(path, index=False, mode='x')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    compare(parser.parse_args().output)
