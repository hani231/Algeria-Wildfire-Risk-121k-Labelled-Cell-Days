"""Permutation à l'intérieur des mois, sur validation, sans sélection de variables."""
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_curve
from threadpoolctl import threadpool_limits
from src.siad03_extensions.data import load_development, new_output, write_json


def permute_within(values, groups, rng):
    values, groups = np.asarray(values), np.asarray(groups)
    out = values.copy()
    for g in np.unique(groups):
        ix = np.flatnonzero(groups == g)
        out[ix] = values[rng.permutation(ix)]
    return out


def run(benchmark, output):
    out = new_output(output); benchmark = Path(benchmark)
    _, val, features, _ = load_development()
    x = val[features]; groups = val.date.dt.month.to_numpy()
    rng = np.random.default_rng(42); records = []
    for name in ['LogisticRegression', 'HistGradientBoosting']:
        model = joblib.load(benchmark/f'{name}.joblib')
        base = average_precision_score(val.label, model.predict_proba(x)[:,1])
        for feature in features:
            changes = []
            for _ in range(5):
                shuffled = x.copy()
                shuffled[feature] = permute_within(x[feature], groups, rng)
                changes.append(base - average_precision_score(val.label, model.predict_proba(shuffled)[:,1]))
            records.append(dict(model=name, feature=feature, ap_drop_mean=np.mean(changes),
                ap_drop_std=np.std(changes, ddof=1), repeats=5, baseline_ap=base))
    result = pd.DataFrame(records); result.to_csv(out/'permutation_month.csv', index=False)
    fig, axes = plt.subplots(1,2,figsize=(12,6))
    for (name, rows), ax in zip(result.groupby('model'), axes):
        rows = rows.sort_values('ap_drop_mean').tail(12)
        ax.barh(rows.feature, rows.ap_drop_mean, xerr=rows.ap_drop_std, color='#355c7d')
        ax.axvline(0,color='black',lw=.8)
        ax.set(title=name, xlabel='Perte d’Average Precision (± écart-type)')
    fig.suptitle('Permutation dans chaque mois de 2024 — descriptive, non causale')
    fig.tight_layout(); fig.savefig(out/'permutation.png',dpi=150); plt.close(fig)
    predictions = pd.read_csv(benchmark/'predictions_validation.csv')
    models = pd.read_csv(benchmark/'metrics.csv').model.tolist()
    fig, axes = plt.subplots(1,3,figsize=(15,4.5))
    for name in models:
        score = predictions[name]
        p,r,_ = precision_recall_curve(predictions.label, score)
        fpr,tpr,_ = roc_curve(predictions.label,score)
        axes[0].plot(r,p,label=name); axes[1].plot(fpr,tpr,label=name)
        cal = pd.read_csv(benchmark/f'{name}_calibration.csv')
        axes[2].plot(cal.predicted,cal.observed,marker='o',label=name)
    axes[0].axhline(predictions.label.mean(),color='gray',ls='--')
    axes[0].set(xlabel='Rappel',ylabel='Précision',title='Precision–Recall (2024)',xlim=(0,1),ylim=(0,1))
    axes[1].plot([0,1],[0,1],'--',color='gray'); axes[1].set(xlabel='Taux de faux positifs',ylabel='Rappel',title='ROC (2024)')
    axes[2].plot([0,1],[0,1],'--',color='gray'); axes[2].set(xlabel='Probabilité moyenne prédite',ylabel='Fréquence observée',title='Calibration (2024)',xlim=(0,1),ylim=(0,1))
    axes[1].legend(fontsize=8); fig.tight_layout(); fig.savefig(out/'performance.png',dpi=150); plt.close(fig)
    write_json(out/'method.json', {'metric':'average_precision (non interpolée, distincte de l’aire trapézoïdale PR)',
        'seed':42, 'repeats':5, 'partition':'validation 2024', 'permutation':'within month, one feature at a time',
        'limits':['Destruction possible de dépendances entre prédicteurs corrélés',
                  'Écart-type des permutations, pas intervalle de confiance populationnel',
                  'Réutilisation de validation pour interprétation uniquement, pas nouvelle sélection',
                  'Aucune attribution causale ; ne prouve pas une généralisation spatiale']})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark', default='results/siad03_extensions/benchmark')
    p.add_argument('--output', default='results/siad03_extensions/explain')
    args = p.parse_args()
    with threadpool_limits(limits=2): run(args.benchmark,args.output)
