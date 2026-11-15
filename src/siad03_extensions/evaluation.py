"""Métriques et incertitude sur l'échantillon de validation, seuil fixé à 0,5."""
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
    confusion_matrix, f1_score, matthews_corrcoef, precision_score, recall_score, roc_auc_score)


def metrics(y, score, threshold=0.5):
    y, score = np.asarray(y), np.asarray(score, dtype=float)
    if (not len(y) or y.shape != score.shape or not np.isin(y, [0, 1]).all()
            or not np.isfinite(score).all() or ((score < 0) | (score > 1)).any()
            or not 0 <= threshold <= 1):
        raise ValueError('Cibles, probabilités ou seuil invalides.')
    pred = (score >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if tp + fn else np.nan
    specificity = tn / (tn + fp) if tn + fp else np.nan
    both = len(np.unique(y)) == 2
    return dict(n=len(y), positives=int(y.sum()), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
        accuracy=accuracy_score(y, pred), precision=precision_score(y, pred, zero_division=0),
        recall=recall_score(y, pred, zero_division=0), f1=f1_score(y, pred, zero_division=0),
        specificity=specificity, balanced_accuracy=(sensitivity + specificity)/2,
        mcc=matthews_corrcoef(y, pred) if both else np.nan,
        roc_auc=roc_auc_score(y, score) if both else np.nan,
        average_precision=average_precision_score(y, score) if y.sum() else np.nan,
        brier=brier_score_loss(y, score))


def calibration(y, score):
    frame = pd.DataFrame({'label': y, 'score': score})
    frame['bin'] = pd.cut(frame.score, np.linspace(0, 1, 11), include_lowest=True)
    return frame.groupby('bin', observed=True).agg(n=('label', 'size'),
        predicted=('score', 'mean'), observed=('label', 'mean')).reset_index()


def grouped_errors(frame, score, column):
    local = frame.copy(); local['score'] = np.asarray(score)
    return pd.DataFrame([{'group': str(k), **metrics(g.label, g.score)}
        for k, g in local.groupby(column, observed=True, dropna=False)])


def cluster_intervals(y, score, groups, repeats=300, seed=42):
    """Bootstrap de cellules entières, conditionnel à 2024 (pas de garantie spatiale)."""
    if repeats < 2:
        raise ValueError('Au moins deux réplications sont requises.')
    y, score, groups = np.asarray(y), np.asarray(score), np.asarray(groups)
    metrics(y, score)
    if len(groups) != len(y) or pd.isna(groups).any():
        raise ValueError('Groupes invalides.')
    unique = np.unique(groups)
    if len(unique) < 2:
        raise ValueError('Au moins deux cellules sont requises.')
    indices = [np.flatnonzero(groups == g) for g in unique]
    rng = np.random.default_rng(seed)
    keys = ['f1', 'average_precision', 'roc_auc', 'brier', 'balanced_accuracy']
    rows = []
    for _ in range(repeats):
        ix = np.concatenate([indices[i] for i in rng.integers(len(unique), size=len(unique))])
        m = metrics(y[ix], score[ix]); rows.append([m[k] for k in keys])
    a = np.asarray(rows)
    return pd.DataFrame([dict(metric=k, low=np.nanquantile(a[:, i], .025),
        high=np.nanquantile(a[:, i], .975), valid_replicates=int(np.isfinite(a[:, i]).sum()),
        repeats=repeats, cells=len(unique)) for i, k in enumerate(keys)])
