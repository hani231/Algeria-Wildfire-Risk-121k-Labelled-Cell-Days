"""Compiler le rapport et contrôler ses tableaux à partir des résultats publiés."""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile

import pandas as pd

from src.models import LOT
from src.siad03_extensions.data import ROOT


def format_value(value):
    return f'{value:.3f}'.replace('.', ',') if isinstance(value, float) else str(value)


def table(frame):
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


def published_tables():
    metrics = pd.read_csv(LOT/'metrics.csv').set_index('model')
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
    diagnostic = pd.read_csv(ROOT/'results/post_freeze/kfold_train/folds.csv')
    paired = diagnostic.groupby('model')[['f1_fit','f1_check']].mean().reindex(metrics.index)
    paired['Chronologique'] = metrics.cv_f1
    paired = paired.rename(columns={'f1_fit':'KFold apprentissage', 'f1_check':'KFold validation'})
    alerts = pd.read_csv(ROOT/'results/post_freeze/alerts_2024/thresholds.csv')
    weather = pd.read_csv(ROOT/'results/post_freeze/development_profiles/erreurs_2024.csv')
    temperature = weather.loc[weather.dimension.eq('temp_max'), ['stratum', 'n', 'tp', 'fp', 'fn', 'tn']].copy()
    temperature['stratum'] = temperature.stratum.str.replace('-inf', '−∞').str.replace('inf', '+∞')
    statistics = []
    for pairing, suffix in [('Cellule et année', 'principal'), ('Cellule, année et mois', 'sensibilite_mois')]:
        effects = pd.read_csv(ROOT/f'results/audit_siad03/statistiques_{suffix}.csv').set_index('variable')
        statistics.append({'Appariement': pairing, 'Température maximale (°C)': effects.at['temp_max', 'ecart_annuel_moyen'],
                           'Humidité moyenne (points)': effects.at['rh_mean', 'ecart_annuel_moyen']})
    return {
        'APPARIEMENTS': pd.DataFrame(statistics),
        'TEMPERATURE': temperature.rename(columns={'stratum': 'Intervalle (°C)', 'n': 'Cellules-jours',
                                                   'tp': 'VP', 'fp': 'FP', 'fn': 'FN', 'tn': 'VN'}),
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


def verify_pdf(pdf):
    """Comparer chaque ligne des tableaux expérimentaux au texte réellement rendu."""
    extracted = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True,
                               capture_output=True, encoding='utf-8').stdout
    lines = {' '.join(line.split()) for line in extracted.splitlines()}
    tables = published_tables()
    for name, frame in tables.items():
        for row in frame.itertuples(index=False, name=None):
            line = ' '.join(format_value(value) for value in row)
            if line not in lines:
                raise ValueError(f'Ligne absente ou différente dans le PDF ({name}) : {line}')
    print(f'{len(tables)} tableaux, {sum(len(frame) for frame in tables.values())} lignes vérifiées.')


def build():
    docs = ROOT/'docs'
    source = (docs/'Rapport_MiniProject.md').read_text()
    for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', source):
        if not (ROOT / image).is_file():
            raise FileNotFoundError(f'Illustration absente du rapport : {image}')
    engine = os.environ.get('PANDOC_PDF_ENGINE', 'xelatex')
    for key, frame in published_tables().items():
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Vérifier le PDF existant avec pdftotext.')
    if parser.parse_args().verify:
        verify_pdf(ROOT / 'docs/Rapport_MiniProject.pdf')
    else:
        build()
