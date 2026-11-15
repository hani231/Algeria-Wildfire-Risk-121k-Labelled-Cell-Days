"""Lecture contrôlée et sorties non destructives des expériences personnelles."""
from pathlib import Path
import hashlib
import json
import pandas as pd
from src.cleaning_guide import clean_data

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {'label', 'split', 'sample_kind', 'n_detections', 'max_frp',
             'days_since_last_fire', 'ndvi_normal', 'ndvi_anomaly', 'year', 'cell_id'}


def load_development(data=None, protocol=None):
    data = Path(data or ROOT / 'Dataset/dataset.csv')
    protocol = Path(protocol or ROOT / 'results/protocole_propose.json')
    config = json.loads(protocol.read_text())
    features = config['features']
    if not features or len(features) != len(set(features)) or FORBIDDEN.intersection(features):
        raise ValueError('Liste de variables vide, répétée ou présentant un risque de fuite.')
    if config['cv_annees_validation'] != [2019, 2020, 2021, 2022, 2023]:
        raise ValueError('Les cinq plis du protocole existant sont requis.')
    # Les lignes de test sont écartées avant nettoyage et statistiques de développement.
    raw = pd.read_csv(data)
    development = raw.loc[raw.split.isin(['train', 'val'])].copy()
    df, report = clean_data(development)
    if not set(features).issubset(df):
        raise ValueError('Prédicteurs manquants.')
    train = df.loc[df.split.eq('train')].sort_values(['date', 'cell_id']).reset_index(drop=True)
    val = df.loc[df.split.eq('val')].sort_values(['date', 'cell_id']).reset_index(drop=True)
    if set(train.year) != set(range(2012, 2024)) or set(val.year) != {2024}:
        raise ValueError('Années de développement incomplètes.')
    report.update(raw_sha256=hashlib.sha256(data.read_bytes()).hexdigest(),
                  protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),
                  test_evaluated=False, n_train=len(train), n_val=len(val))
    return train, val, features, report


def new_output(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
