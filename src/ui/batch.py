"""Import CSV numérique borné pour les pipelines locaux de Prediction Studio."""
import csv
import io

import pandas as pd
import streamlit as st

from src.ui.prediction_enhanced import example_csv, predict_batch, score_distribution

MAX_BYTES = 1024 * 1024
MAX_ROWS = 1000


def read_batch(payload, features):
    if len(payload) > MAX_BYTES:
        raise ValueError('Le fichier dépasse 1 Mio.')
    try:
        reader = csv.reader(io.StringIO(payload.decode('utf-8-sig'), newline=''), strict=True)
        header = next(reader, [])
        expected = set(features)
        siad03_export = expected | {'observation', 'classe', 'score_classe_1', 'modele', 'seuil'}
        iasd17_export = expected | {'score', 'prediction', 'alerte'}
        schemas = (expected, iasd17_export, siad03_export, siad03_export | {'tranche_score'})
        if len(header) != len(set(header)) or set(header) not in schemas:
            raise ValueError('En-tête incorrect. Utilisez exactement les colonnes du modèle CSV.')
        rows = []
        for number, row in enumerate(reader, start=1):
            if number > MAX_ROWS:
                raise ValueError('Le fichier dépasse 1 000 observations.')
            if len(row) != len(header):
                raise ValueError(f'Observation {number} : nombre de champs incorrect.')
            rows.append(row)
    except (UnicodeError, csv.Error) as error:
        raise ValueError('CSV illisible. Utilisez UTF-8, la virgule et le point décimal.') from error
    if not rows:
        raise ValueError('Le fichier doit contenir au moins une observation.')
    return pd.DataFrame(rows, columns=header)[list(features)]


def score_batch(payload, model, threshold, summary, *, allow_missing=False):
    frame = read_batch(payload, model.feature_names_in_)
    return predict_batch(model, frame, threshold, summary=summary, allow_missing=allow_missing)


def batch_panel(name, model, threshold, summary):
    st.subheader('Classifier un lot de cellules-jours')
    st.write('Utilisez les 24 colonnes du modèle CSV, en UTF-8, avec une virgule entre les champs '
             'et un point décimal. Les unités et les plages sont celles du formulaire.')
    st.download_button('Télécharger un exemple CSV', example_csv(model.feature_names_in_),
                       'exemple_cellule_jour.csv', 'text/csv', on_click='ignore')
    allow_missing = st.checkbox('Accepter les mesures manquantes', value=False,
                                help='Les champs vides utilisent le traitement natif du modèle '
                                     'ou l’imputation apprise sur le train. Une ligne entièrement vide est refusée.')
    st.caption('Un export complet du studio peut être réimporté. Seules les 24 mesures '
               'alimentent le modèle choisi et tous les résultats sont recalculés.')
    upload = st.file_uploader('Importer le CSV (1 Mio et 1 000 observations maximum)', type=['csv'])
    if upload is None:
        return
    try:
        result = score_batch(upload.getvalue(), model, threshold, summary, allow_missing=allow_missing)
    except ValueError as error:
        st.error(str(error))
        return
    st.write(f'{len(result)} observations classées · {int(result.classe.sum())} alertes · '
             f'{name} au seuil {threshold:.2f}')
    st.caption('Le score décrit une détection dans la population échantillonnée avec la météo du jour.')
    if 'tranche_score' in result:
        score_distribution(result)
    st.dataframe(result[['observation', 'classe', 'score_classe_1', 'tranche_score']] if 'score_classe_1' in result
                 else result[['observation', 'classe']], hide_index=True, width='stretch')
    export = result.assign(modele=name, seuil=threshold).to_csv(index=False)
    st.download_button('Télécharger les prédictions CSV', export, 'predictions.csv',
                       'text/csv', on_click='ignore')
