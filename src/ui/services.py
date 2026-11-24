"""Données et pipelines versionnés pour l'interface SIAD03."""
import json
import warnings
from pickle import UnpicklingError
from sklearn.exceptions import InconsistentVersionWarning
from src.models import CONFIG, LOT, MANDATORY
from src.data_quality import coherence_counts
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from src.siad03_extensions.data import ROOT, load_development
from src.siad03_nb.contract import validate_protocol

BENCH = ROOT / 'results/siad03_extensions/benchmark'
BATCHES = {name: LOT for name in ('GaussianNB', *MANDATORY)}
BATCHES.update({name: BENCH for name in ('LogisticRegression', 'HistGradientBoosting')})
ARTIFACTS = {name: folder/(name + '.joblib') for name, folder in BATCHES.items()}


def decision():
    return json.loads((LOT/'decision.json').read_text())


@st.cache_data(show_spinner='Chargement des observations d’entraînement…')
def training():
    return load_development(protocol=CONFIG)[0]


@st.cache_data
def comparison():
    tables = []
    for folder in dict.fromkeys(BATCHES.values()):
        table = pd.read_csv(folder/'metrics.csv')
        tables.append(table.loc[table.model.map(BATCHES).eq(folder)])
    return pd.concat(tables, ignore_index=True).set_index('model')


def pipeline(name):
    path = ARTIFACTS[name]
    return _load_pipeline(path, path.stat().st_mtime_ns)


@st.cache_resource(show_spinner='Lecture du pipeline sauvegardé…')
def _load_pipeline(path, modified):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', InconsistentVersionWarning)
            model = joblib.load(path)
    except (InconsistentVersionWarning, EOFError, UnpicklingError, ImportError, AttributeError, KeyError) as error:
        raise ValueError(f'Artefact incompatible ou illisible ({path.name}) : {error}') from error
    protocol = validate_protocol(json.loads(CONFIG.read_text()))
    if list(getattr(model, 'feature_names_in_', [])) != protocol['features']:
        raise ValueError('Le schéma du modèle diffère du protocole.')
    if set(getattr(model, 'classes_', [])) != {0, 1} or not callable(getattr(model, 'predict', None)):
        raise ValueError('Pipeline incompatible avec la classification binaire.')
    return model


def classify(model, values, threshold=0.5):
    columns = list(model.feature_names_in_)
    if set(values) != set(columns):
        raise ValueError('Entrées incomplètes ou inattendues.')
    frame = pd.DataFrame([values], columns=columns)
    labels, scores = classify_rows(model, frame, threshold)
    return int(labels[0]), None if scores is None else float(scores[0])


def classify_rows(model, frame, threshold):
    """Valider tout le lot avant l'unique appel au pipeline déjà chargé."""
    columns = list(model.feature_names_in_)
    if frame.empty or not frame.columns.is_unique or set(frame.columns) != set(columns):
        raise ValueError('Entrées incomplètes ou inattendues.')
    try:
        frame = frame[columns].astype(float)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('Chaque mesure doit être numérique.') from error
    if not np.isfinite(frame).all().all():
        raise ValueError('Chaque mesure doit être renseignée et finie.')
    violations = [key.replace('_', ' ') for key, count in coherence_counts(frame).items() if count]
    if violations:
        raise ValueError('Mesures physiquement incohérentes : ' + ', '.join(violations))
    for key in ('doy', 'ndvi_stale_days', 'days_since_rain_1mm'):
        if frame[key].mod(1).ne(0).any():
            raise ValueError(f'{key} doit être un nombre entier de jours.')
    if not frame.doy.between(1, 366).all():
        raise ValueError('Le jour de l’année doit être compris entre 1 et 366.')
    if not hasattr(model, 'predict_proba'):
        return model.predict(frame), None
    scores = model.predict_proba(frame)[:, list(model.classes_).index(1)]
    return (scores >= threshold).astype(int), scores


@st.cache_data
def input_summary(features):
    data = training()[list(features)]
    complete = data.dropna()
    if complete.empty:
        raise ValueError('Aucune observation complète pour initialiser les mesures du formulaire.')
    return pd.DataFrame({'initial': complete.iloc[0], 'minimum': data.min(), 'maximum': data.max()})
