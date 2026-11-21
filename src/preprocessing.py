"""Préparation commune du lot final. Les expériences historiques gardent leur contrat."""
import json
from src.siad03_nb.contract import load_inputs, validate_protocol
from src.siad03_extensions.data import ROOT

CONFIG = ROOT/'config/protocole.json'


def read_protocol():
    cfg = validate_protocol(json.loads(CONFIG.read_text(encoding='utf-8')))
    if {'cell_id', 'date', 'lat', 'lon', 'year'}.intersection(cfg['features']):
        raise ValueError('Une métadonnée géographique ou temporelle figure dans X.')
    return cfg


def development_inputs():
    cfg = read_protocol()
    train, val, features, folds, provenance = load_inputs(protocol=CONFIG)
    if provenance['raw_sha256'] != cfg['raw_sha256']:
        raise ValueError('Empreinte du dataset incompatible avec ce protocole.')
    return train, val, features, folds, provenance
