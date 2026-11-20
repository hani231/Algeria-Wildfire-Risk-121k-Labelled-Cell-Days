"""Données et pipelines versionnés pour l'interface SIAD03."""
import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from src.siad03_extensions.data import ROOT, load_development
from src.siad03_nb.contract import validate_protocol

BENCH = ROOT / 'results/siad03_extensions/benchmark'
NB = ROOT / 'results/siad03_nb/run_01'
ARTIFACTS = {
    'GaussianNB': NB / 'GaussianNB.joblib',
    'Zero-R': NB / 'Zero-R.joblib',
    'LogisticRegression': BENCH / 'LogisticRegression.joblib',
    'HistGradientBoosting': BENCH / 'HistGradientBoosting.joblib',
}


@st.cache_data
def training():
    return load_development()[0]


@st.cache_data
def comparison():
    historical = pd.read_csv(BENCH / 'metrics.csv')
    personal = pd.read_csv(NB / 'metrics.csv')
    return pd.concat([personal, historical[~historical.model.isin(personal.model)]],
                     ignore_index=True).set_index('model')


@st.cache_resource
def pipeline(name):
    model = joblib.load(ARTIFACTS[name])
    protocol = validate_protocol(json.loads((ROOT / 'results/protocole_propose.json').read_text()))
    if list(model.feature_names_in_) != protocol['features']:
        raise ValueError('Le schéma du modèle diffère du protocole.')
    return model


def classify(model, values):
    columns = list(model.feature_names_in_)
    if set(values) != set(columns):
        raise ValueError('Entrées incomplètes ou inattendues.')
    frame = pd.DataFrame([values], columns=columns, dtype=float)
    if not np.isfinite(frame).all().all():
        raise ValueError('Une valeur numérique est invalide.')
    for low, high in [('temp_min','temp_mean'), ('temp_mean','temp_max'),
                      ('rh_min','rh_mean'), ('wind_mean','wind_max')]:
        if values[low] > values[high]:
            raise ValueError(f'{low} doit être inférieur ou égal à {high}.')
    label = int(model.predict(frame)[0])
    score = float(model.predict_proba(frame)[0, list(model.classes_).index(1)])
    return label, score
