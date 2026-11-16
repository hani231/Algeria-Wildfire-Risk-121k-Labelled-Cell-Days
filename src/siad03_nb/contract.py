"""Vérifier le contrat existant sans définir un nouveau protocole commun."""
import json
from pathlib import Path

from src.siad03_extensions.data import ROOT, FORBIDDEN, load_development
from src.train_decision_tree import build_temporal_splits


def validate_protocol(config):
    expected = dict(train='2012-2023', validation='2024', test_reserve='2025',
                    metrique_principale='f1_classe_1',
                    cv_annees_validation=[2019, 2020, 2021, 2022, 2023])
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValueError(f'Contrat commun incompatible : {key}')
    features = config.get('features')
    if (not isinstance(features, list) or not features
            or not all(isinstance(c, str) for c in features)
            or len(features) != len(set(features))
            or FORBIDDEN.intersection(features) or 'date' in features):
        raise ValueError('Prédicteurs invalides ou fuite potentielle.')
    return config


def load_inputs(data=None, protocol=None):
    protocol = Path(protocol or ROOT / 'results/protocole_propose.json')
    config = validate_protocol(json.loads(protocol.read_text(encoding='utf-8')))
    train, val, features, provenance = load_development(data=data, protocol=protocol)
    folds = build_temporal_splits(train, config['cv_annees_validation'])
    if train.date.max() >= val.date.min():
        raise ValueError('Validation non postérieure au train.')
    provenance['protocol_status'] = config['statut']
    return train, val, features, folds, provenance
