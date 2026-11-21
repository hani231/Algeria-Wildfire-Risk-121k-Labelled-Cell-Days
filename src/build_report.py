"""Compiler le rapport éditable et ses graphiques à partir des résultats versionnés."""
import json
from pathlib import Path
import subprocess
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

from src.models import LOT
from src.siad03_extensions.data import ROOT


def table(frame):
    def format_value(value):
        return f'{value:.3f}'.replace('.', ',') if isinstance(value, float) else str(value)
    lines = [list(frame.columns), ['---']*len(frame.columns)]
    lines.extend([[format_value(value) for value in row] for row in frame.itertuples(index=False, name=None)])
    return '\n'.join('| ' + ' | '.join(row) + ' |' for row in lines)


def build():
    docs = ROOT/'docs'
    metrics = pd.read_csv(LOT/'metrics.csv').set_index('model')
    scores = pd.read_csv(LOT/'predictions_validation.csv')
    if not scores.year.eq(2024).all():
        raise ValueError('La figure de développement requiert les prédictions de 2024.')
    fig, axes = plt.subplots(1, 2, figsize=(9.3, 3.7), layout='constrained')
    for name in metrics.index:
        fp, tp, _ = roc_curve(scores.label, scores[name])
        precision, recall, _ = precision_recall_curve(scores.label, scores[name], drop_intermediate=True)
        axes[0].plot(fp, tp, label=name, linewidth=1.4)
        axes[1].step(recall, precision, where='post', linewidth=1.2)
    axes[0].plot([0,1],[0,1], ':', color='gray')
    axes[1].axhline(scores.label.mean(), ls=':', color='gray')
    axes[0].set(xlabel='Taux de faux positifs', ylabel='Rappel', title='Courbes ROC')
    axes[1].set(xlabel='Rappel', ylabel='Précision', title='Courbes précision–rappel')
    axes[0].legend(fontsize=8)
    for ax in axes:
        ax.set(xlim=(0,1),ylim=(0,1))
        ax.grid(alpha=.2)
    fig.savefig(LOT/'courbes_2024.png', dpi=170)
    plt.close(fig)
    final = json.loads((ROOT/'results/test_final/result.json').read_text())
    columns = {'accuracy':'Acc.', 'precision':'Préc.', 'recall':'Rappel', 'f1':'F1',
               'balanced_accuracy':'Acc. éq.', 'roc_auc':'ROC', 'average_precision':'AP'}
    core = metrics.rename_axis('Modèle').reset_index()
    ablation = pd.read_csv(LOT/'ablation_train.csv').groupby('groupe',sort=False)[['f1','average_precision']].mean()
    tables = {
        'SCORES': core[['Modèle',*columns]].rename(columns=columns),
        'COUTS': core[['Modèle','cv_f1','search_seconds','fit_seconds','predict_seconds']].rename(columns={
            'cv_f1':'F1 CV','search_seconds':'Recherche (s)','fit_seconds':'Ajustement (s)','predict_seconds':'Scores (s)'}),
        'CONFUSIONS': core[['Modèle','tn','fp','fn','tp']].rename(columns={'tn':'VN','fp':'FP','fn':'FN','tp':'VP'}),
        'ABLATION': ablation.rename_axis('Variables').reset_index().rename(columns={'f1':'F1 moyen','average_precision':'AP moyenne'}),
        'TEST': pd.DataFrame([{label:final[key] for key,label in columns.items()}]),
    }
    source = (docs/'Rapport_MiniProject.md').read_text()
    for key, frame in tables.items():
        source = source.replace('{{'+key+'}}', table(frame))
    with tempfile.TemporaryDirectory() as folder:
        expanded = Path(folder)/'report.md'
        expanded.write_text(source,encoding='utf-8')
        subprocess.run(['pandoc',str(expanded),'--pdf-engine=xelatex','-o',str(docs/'Rapport_MiniProject.pdf')],
                       cwd=ROOT, check=True)


if __name__ == '__main__':
    build()
