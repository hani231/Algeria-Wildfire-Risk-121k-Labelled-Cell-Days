"""Ouvrir le test final uniquement pour la décision de développement versionnée."""
import argparse
import json
from pathlib import Path
import subprocess

import joblib
import pandas as pd

from src.cleaning_guide import clean_data
from src.models import CONFIG, LOT, digest
from src.siad03_extensions.data import ROOT, new_output, write_json
from src.siad03_extensions.evaluation import metrics
from src.siad03_nb.contract import validate_protocol


def evaluate(output):
    decision_file = LOT/'decision.json'
    relative = decision_file.relative_to(ROOT).as_posix()
    committed = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'HEAD:{relative}'])
    if committed != decision_file.read_bytes():
        raise ValueError('La décision doit être enregistrée dans Git avant le test.')
    decision = json.loads(committed)
    cfg = validate_protocol(json.loads(CONFIG.read_text()))
    artifact = LOT/(decision['model']+'.joblib')
    data = ROOT/'Dataset/dataset.csv'
    if (decision['refit'] or digest(artifact) != decision['sha256']
            or digest(CONFIG) != decision['config_sha256'] or digest(data) != decision['raw_sha256']):
        raise ValueError('Le gel du modèle, du dataset ou du protocole a changé.')
    raw = pd.read_csv(data)
    mask = raw.split.eq('test')
    if not mask.equals(raw.year.eq(2025)):
        raise ValueError('Partition finale invalide.')
    test, _ = clean_data(raw.loc[mask])
    score = joblib.load(artifact).predict_proba(test[cfg['features']])[:,1]
    pred = test[['date','cell_id','year','label']].assign(score=score, prediction=score>=decision['threshold'])
    result = metrics(test.label, score, decision['threshold'])
    out = new_output(output)
    pred.to_csv(out/'predictions.csv', index=False)
    freeze = subprocess.check_output(['git','-C',str(ROOT),'log','-1','--format=%H','--',relative],text=True).strip()
    write_json(out/'result.json', dict(model=decision['model'], threshold=decision['threshold'],
                                      freeze_commit=freeze, **result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    evaluate(parser.parse_args().output)
