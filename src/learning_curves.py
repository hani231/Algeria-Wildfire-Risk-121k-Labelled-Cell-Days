"""Sensibilité post-gel à la taille du train, mesurée exclusivement sur 2024."""
import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

from src.models import LOT, candidates, limited
from src.preprocessing import development_inputs, read_protocol
from src.siad03_extensions.data import new_output


def run(output):
    train, validation, features, _, _ = development_inputs()
    protocol = read_protocol()
    manifest = json.loads((LOT / 'manifest.json').read_text())['models']
    folder = new_output(output)
    rows = []
    for name in ('K-NN', 'SVM'):
        cap = protocol['train_caps'][name]
        for size in (cap // 4, cap // 2, cap):
            for seed in (42, 43, 44):
                indices = limited(np.arange(len(train)), train.label, size, seed)
                model, _ = candidates(name, protocol['seed'])
                model.set_params(**manifest[name]['params'])
                start = perf_counter()
                model.fit(train.iloc[indices][features], train.label.iloc[indices])
                fitted = perf_counter()
                scores = model.predict_proba(validation[features])[:, 1]
                scored = perf_counter()
                rows.append(dict(model=name, n_fit=size, seed=seed, year=2024,
                                 threshold=0.5, f1=f1_score(validation.label, scores >= 0.5),
                                 fit_seconds=fitted-start, predict_seconds=scored-fitted))
    pd.DataFrame(rows).to_csv(folder / 'learning_curves.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
