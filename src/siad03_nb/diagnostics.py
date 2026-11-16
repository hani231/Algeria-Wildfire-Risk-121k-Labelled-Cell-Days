"""Figures des expériences personnelles, exclusivement depuis les résultats sauvegardés."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay, ConfusionMatrixDisplay
from src.siad03_extensions.data import new_output


def run(experiment, output):
    source, out = Path(experiment), new_output(output)
    cv = pd.read_csv(source / 'search.csv').sort_values('param_model__var_smoothing')
    pred = pd.read_csv(source / 'predictions_2024.csv')
    if not pred.year.eq(2024).all():
        raise ValueError('Ces figures sont réservées à la validation 2024.')
    fig, ax = plt.subplots(figsize=(8, 4))
    x = cv.param_model__var_smoothing
    ax.semilogx(x, cv.mean_train_f1, marker='.', label='Train moyen')
    ax.semilogx(x, cv.mean_test_f1, marker='.', label='CV temporelle moyenne')
    ax.fill_between(x, cv.mean_test_f1-cv.std_test_f1,
                    cv.mean_test_f1+cv.std_test_f1, alpha=.2, label='± 1 écart-type entre plis (pas un IC)')
    ax.set(xlabel='var_smoothing', ylabel='F1 classe 1', title='Réglage NB exclusivement sur les cinq plis train')
    ax.legend(); fig.tight_layout(); fig.savefig(out / 'search.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for name in ['Zero-R', 'GaussianNB']:
        PrecisionRecallDisplay.from_predictions(pred.label, pred[name], name=name, ax=axes[0])
        RocCurveDisplay.from_predictions(pred.label, pred[name], name=name, ax=axes[1])
    axes[0].axhline(pred.label.mean(), ls=':', color='gray', label='Prévalence 2024')
    axes[0].legend(); axes[0].set_title('Validation 2024 — précision/rappel (AP)')
    axes[1].set_title('Validation 2024 — ROC')
    fig.tight_layout(); fig.savefig(out / 'curves.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for name, ax in zip(['Zero-R', 'GaussianNB'], axes):
        ConfusionMatrixDisplay.from_predictions(pred.label, pred[name].ge(.5), labels=[0,1], ax=ax, colorbar=False)
        ax.set_title(name + ' — validation 2024')
    fig.tight_layout(); fig.savefig(out / 'confusion.png', dpi=150); plt.close(fig)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); run(args.experiment, args.output)
