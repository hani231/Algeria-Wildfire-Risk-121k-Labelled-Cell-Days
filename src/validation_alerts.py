"""Décrire les alertes sur les scores publiés de validation, sans ajustement."""
import argparse
import json
from pathlib import Path

import pandas as pd

from src.models import CONFIG, LOT
from src.siad03_extensions.evaluation import calibration, metrics


def summarize_alerts(frame, model, frozen_threshold, thresholds):
    dates = pd.to_datetime(frame.date, errors='raise')
    if frame.empty or not (frame.year.eq(2024) & dates.dt.year.eq(2024)).all():
        raise ValueError('Les scores doivent provenir exclusivement de 2024.')
    if frame[['cell_id', 'date']].isna().any().any() or frame.duplicated(['cell_id', 'date']).any():
        raise ValueError('Clé cellule-jour absente ou dupliquée.')

    def counts(group, threshold):
        measures = metrics(group.label, group[model], threshold)
        return {key: measures[key] for key in
                ('n', 'positives', 'tn', 'fp', 'fn', 'tp', 'precision', 'recall', 'f1')}

    operating = pd.DataFrame([{'threshold': t, **counts(frame, t)} for t in thresholds])
    monthly = pd.DataFrame([{'month': month, **counts(group, frozen_threshold)}
                            for month, group in frame.groupby(dates.dt.month)])
    reliability = calibration(frame.label, frame[model])
    return {'thresholds': operating, 'months': monthly, 'reliability': reliability}


def published_alerts():
    decision = json.loads((LOT / 'decision.json').read_text())
    config = json.loads(CONFIG.read_text())
    scores = pd.read_csv(LOT / 'predictions_validation.csv')
    return summarize_alerts(scores, decision['model'], decision['threshold'], config['thresholds'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Nouveau dossier de sortie')
    destination = parser.parse_args().output
    tables = published_alerts()
    destination.mkdir(parents=True, exist_ok=False)
    for name, table in tables.items():
        table.to_csv(destination / f'{name}.csv', index=False)
