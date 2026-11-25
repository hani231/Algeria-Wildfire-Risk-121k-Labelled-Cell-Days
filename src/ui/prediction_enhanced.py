"""Studio avancé IASD17 : import CSV par lots, alertes et export des prédictions."""
import io
import json
import numpy as np
import pandas as pd
import streamlit as st
from src.data_quality import coherence_counts
from src.explainability.alert_levels import alert_labels
from src.ui.services import ARTIFACTS, CONFIG, decision, pipeline, training

ALERT_ORDER = ('Faible', 'Modéré', 'Élevé', 'Critique')


def protocol_features() -> list:
    return list(json.loads(CONFIG.read_text(encoding='utf-8'))['features'])


def validate_batch(frame: pd.DataFrame, features) -> pd.DataFrame:
    """Contrôle le schéma et les mesures d'un CSV ; renvoie les colonnes du protocole."""
    expected = list(features)
    if frame is None or len(frame) == 0:
        raise ValueError('Le fichier ne contient aucune observation.')
    missing = [col for col in expected if col not in frame.columns]
    if missing:
        raise ValueError('Colonnes manquantes : ' + ', '.join(missing) + '.')
    present = [col for col in frame.columns if col in set(expected)]
    if present != expected:
        for position, (got, want) in enumerate(zip(present, expected), start=1):
            if got != want:
                raise ValueError(f'Ordre des colonnes invalide : position {position} : '
                                 f'{got} au lieu de {want}.')
        raise ValueError('Ordre des colonnes invalide.')
    data = frame.loc[:, expected].copy()
    for col in expected:
        coerced = pd.to_numeric(data[col], errors='coerce')
        invalid = data[col].notna() & coerced.isna()
        if invalid.any():
            raise ValueError(f'Colonne non numérique : {col} ({int(invalid.sum())} valeurs).')
        data[col] = coerced
    if np.isinf(data.to_numpy(dtype=float)).any():
        raise ValueError('Valeurs infinies détectées dans le fichier.')
    violations = [key.replace('_', ' ') for key, count in coherence_counts(data).items() if count]
    if violations:
        raise ValueError('Mesures physiquement incohérentes : ' + ', '.join(violations))
    for col in ('doy', 'ndvi_stale_days', 'days_since_rain_1mm'):
        values = data[col].dropna()
        if ((values % 1) != 0).any():
            raise ValueError(f'{col} doit être un nombre entier de jours.')
    if not data['doy'].dropna().between(1, 366).all():
        raise ValueError('Le jour de l’année doit être compris entre 1 et 366.')
    return data


def predict_batch(model, frame: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Classe chaque ligne et ajoute les colonnes score, prediction et alerte."""
    features = list(model.feature_names_in_)
    values = validate_batch(frame, features)
    classes = list(model.classes_)
    proba = model.predict_proba(values)[:, classes.index(1)]
    out = frame.copy()
    out['score'] = proba
    out['prediction'] = (proba >= threshold).astype(int)
    out['alerte'] = alert_labels(proba)
    return out


def example_csv(features) -> bytes:
    """Modèle de colonnes : en-têtes du protocole et une ligne d'exemple."""
    sample = training()[list(features)].dropna().iloc[:1]
    buffer = io.StringIO()
    sample.to_csv(buffer, index=False)
    return buffer.getvalue().encode('utf-8')


def advanced_studio():
    """Import d'un CSV, distribution des alertes et téléchargement des prédictions."""
    names = [name for name, path in ARTIFACTS.items() if path.is_file()]
    if not names:
        return
    name = st.selectbox('Pipeline', names, key='batch_model')
    final = decision()
    threshold = final['threshold'] if final['model'] == name else .5
    features = protocol_features()
    st.caption(f'Seuil appliqué : {threshold:.2f}. Colonnes exactes du protocole, une observation par ligne. '
               'Les valeurs manquantes sont imputées par le pipeline, comme à l’entraînement.')
    st.download_button('Télécharger le modèle de colonnes', data=example_csv(features),
                       file_name='modele_colonnes.csv', mime='text/csv', key='batch_template')
    upload = st.file_uploader('Fichier CSV à classer', type='csv', key='batch_file',
                              help='24 colonnes du protocole, dans l’ordre exact.')
    if upload is None:
        st.caption('Aucun fichier chargé : aucune prédiction par lot n’est disponible.')
        return
    try:
        frame = pd.read_csv(upload)
        model = pipeline(name)
        out = predict_batch(model, frame, threshold)
    except ValueError as error:
        st.error(str(error))
        return
    st.success(f'{len(out):,} observations classées en quatre niveaux d’alerte.')
    counts = out['alerte'].value_counts()
    for column, label in zip(st.columns(4), ALERT_ORDER):
        column.metric(label, int(counts.get(label, 0)))
    st.dataframe(out, width='stretch')
    st.download_button('Télécharger les prédictions',
                       data=out.to_csv(index=False).encode('utf-8'),
                       file_name='predictions.csv', mime='text/csv', key='batch_download')
