"""Compiler le rapport éditable et ses graphiques à partir des résultats versionnés."""
import json
import os
import re
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
    # Tables compactes : les en-têtes et noms de modèles gardent leur largeur naturelle.
    from string import Template
    def escape(value):
        return value.replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')
    rows = [list(frame.columns), *frame.itertuples(index=False, name=None)]
    body = '\n'.join(' & '.join(escape(format_value(v)) for v in row) + r' \\'
                     for row in rows)
    return Template(r"""\begin{center}\small
\begin{tabular}{$align}
\hline
$body
\hline
\end{tabular}
\end{center}""").substitute(align='l'+'r'*(len(frame.columns)-1), body=body)


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
    years = json.loads((ROOT/'config/protocole.json').read_text())['cv_annees_validation']
    folds = []
    for name in metrics.index:
        search = pd.read_csv(LOT/f'{name}_cv.csv')
        selected = search.loc[search.mean_test_score.idxmax()]
        folds.append({'Modèle': name, **{str(year): selected[f'split{i}_test_score']
                      for i, year in enumerate(years)}, 'Moy.': selected.mean_test_score,
                      'Éc. type': selected.std_test_score})
    sizes = pd.read_csv(ROOT/'results/post_freeze/size_2024/learning_curves.csv')
    summary = sizes.groupby(['model', 'n_fit']).agg(
        F1=('f1', 'mean'), dispersion=('f1', 'std'), fit=('fit_seconds', 'mean'),
        predict=('predict_seconds', 'mean')).reset_index()
    summary.columns = ['Modèle', 'Lignes', 'F1', 'Éc. type', 'Ajust. (s)', 'Préd. (s)']
    fig, ax = plt.subplots(figsize=(4, 2.5), layout='constrained')
    matrix = [[final['tn'], final['fp']], [final['fn'], final['tp']]]
    ax.imshow(matrix, cmap='Blues')
    for i, row in enumerate(matrix):
        for j, count in enumerate(row):
            ax.text(j, i, str(count), ha='center', va='center',
                    color='white' if count > final['fp']*.65 else 'black')
    ax.set(xticks=[0,1], yticks=[0,1], xlabel='Classe prédite', ylabel='Classe observée')
    fig.savefig(docs/'confusion_2025.png', dpi=160)
    plt.close(fig)
    diagnostic = pd.read_csv(ROOT/'results/post_freeze/kfold_train/folds.csv')
    paired = diagnostic.groupby('model')[['f1_fit','f1_check']].mean().reindex(metrics.index)
    paired['Chronologique'] = metrics.cv_f1
    paired = paired.rename(columns={'f1_fit':'KFold apprentissage', 'f1_check':'KFold validation'})
    alerts = pd.read_csv(ROOT/'results/post_freeze/alerts_2024/thresholds.csv')
    tables = {
        'ALERTES': alerts[['threshold', 'tp', 'fp', 'fn', 'precision', 'recall']].rename(
            columns={'threshold': 'Seuil', 'tp': 'VP', 'fp': 'FP', 'fn': 'FN',
                     'precision': 'Précision', 'recall': 'Rappel'}),
        'KFOLD': paired.rename_axis('Modèle').reset_index(),
        'PLIS': pd.DataFrame(folds), 'TAILLES': summary,
        'SCORES': core[['Modèle',*columns]].rename(columns=columns),
        'COUTS': core[['Modèle','cv_f1','search_seconds','fit_seconds','predict_seconds']].rename(columns={
            'cv_f1':'F1 CV','search_seconds':'Recherche (s)','fit_seconds':'Ajustement (s)','predict_seconds':'Scores (s)'}),
        'CONFUSIONS': core[['Modèle','tn','fp','fn','tp']].rename(columns={'tn':'VN','fp':'FP','fn':'FN','tp':'VP'}),
        'ABLATION': ablation.rename_axis('Variables').reset_index().rename(columns={'f1':'F1 moyen','average_precision':'AP moyenne'}),
        'TEST': pd.DataFrame([{label:final[key] for key,label in columns.items()}]),
    }
    source = (docs/'Rapport_MiniProject.md').read_text()
    for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', source):
        if not (ROOT / image).is_file():
            raise FileNotFoundError(f'Illustration absente du rapport : {image}')
    engine = os.environ.get('PANDOC_PDF_ENGINE', 'xelatex')
    for key, frame in tables.items():
        source = source.replace('{{'+key+'}}', frame.to_html(index=False, float_format=lambda value: f'{value:.3f}'.replace('.', ','))
                                if engine == 'weasyprint' else table(frame))
    with tempfile.TemporaryDirectory() as folder:
        expanded = Path(folder)/'report.md'
        if engine == 'weasyprint':
            source = source.replace(r'\newpage', '<div style="break-after:page"></div>')
            html = subprocess.run(['pandoc','--from=markdown','--to=html5','--standalone',
                                   '--mathml', '--css', 'docs/rapport.css'], input=source, text=True, capture_output=True, check=True)
            from weasyprint import HTML
            HTML(string=html.stdout, base_url=str(ROOT)+'/').write_pdf(
                docs/'Rapport_MiniProject.pdf')
            return
        expanded.write_text(source,encoding='utf-8')
        subprocess.run(['pandoc',str(expanded),'--pdf-engine='+os.environ.get('PANDOC_PDF_ENGINE','xelatex'),'-o',str(docs/'Rapport_MiniProject.pdf')],
                       cwd=ROOT, check=True)


if __name__ == '__main__':
    build()
