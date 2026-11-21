"""Sensibilité post-gel à la taille du train, mesurée exclusivement sur 2024."""
import argparse
import json
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
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
    frame = pd.DataFrame(rows)
    frame.to_csv(folder / 'learning_curves.csv', index=False)
    plot_sizes(frame, folder)


def plot_sizes(frame, folder):
    fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True, layout='constrained')
    for ax, (name, rows) in zip(axes, frame.groupby('model')):
        for seed, sample in rows.groupby('seed'):
            ax.plot(sample.n_fit, sample.f1, marker='o', label=str(seed))
        ax.set(title=name, xlabel='Lignes du train', xticks=sorted(rows.n_fit.unique()))
    axes[0].set_ylabel('F1 en validation 2024 (seuil 0,50)')
    axes[1].legend(title='Graine')
    fig.savefig(folder/'learning_curves.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    with threadpool_limits(limits=1):
        run(parser.parse_args().output)
