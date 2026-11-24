"""Import CSV numérique borné pour les pipelines locaux de Prediction Studio."""
import csv
import io

import pandas as pd
import streamlit as st

from src.ui.services import classify_rows

MAX_BYTES = 1024 * 1024
MAX_ROWS = 1000


def read_batch(payload, features):
    if len(payload) > MAX_BYTES:
        raise ValueError('Le fichier dépasse 1 Mio.')
    try:
        reader = csv.reader(io.StringIO(payload.decode('utf-8-sig'), newline=''), strict=True)
        header = next(reader, [])
        if len(header) != len(features) or set(header) != set(features):
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
    return pd.DataFrame(rows, columns=header)[features]


def score_batch(payload, model, threshold, summary):
    features = list(model.feature_names_in_)
    frame = read_batch(payload, features)
    try:
        frame = frame.astype(float)
    except (ValueError, OverflowError) as error:
        raise ValueError('Chaque champ doit contenir un nombre décimal.') from error
    outside = frame.lt(summary.minimum, axis='columns') | frame.gt(summary.maximum, axis='columns')
    if outside.any().any():
        i, j = outside.to_numpy().nonzero()
        raise ValueError(f'Observation {i[0] + 1} : {features[j[0]]} sort de la plage du formulaire.')
    labels, scores = classify_rows(model, frame, threshold)
    result = frame.assign(classe=labels)
    if scores is not None:
        result['score_classe_1'] = scores
    result.insert(0, 'observation', range(1, len(result) + 1))
    return result


def batch_panel(name, model, threshold, summary):
    st.subheader('Classifier un lot de cellules-jours')
    st.write('Utilisez les 24 colonnes du modèle CSV, en UTF-8, avec une virgule entre les champs '
             'et un point décimal. Les unités et les plages sont celles du formulaire.')
    st.download_button('Télécharger un exemple CSV', summary.initial.to_frame().T.to_csv(index=False),
                       'exemple_cellule_jour.csv', 'text/csv', on_click='ignore')
    upload = st.file_uploader('Importer le CSV (1 Mio et 1 000 observations maximum)', type=['csv'])
    if upload is None:
        return
    try:
        result = score_batch(upload.getvalue(), model, threshold, summary)
    except ValueError as error:
        st.error(str(error))
        return
    st.write(f'{len(result)} observations classées · {int(result.classe.sum())} alertes · '
             f'{name} au seuil {threshold:.2f}')
    st.caption('Le score décrit une détection dans la population échantillonnée avec la météo du jour.')
    st.dataframe(result[['observation', 'classe', 'score_classe_1']] if 'score_classe_1' in result
                 else result[['observation', 'classe']], hide_index=True, width='stretch')
    export = result.assign(modele=name, seuil=threshold).to_csv(index=False)
    st.download_button('Télécharger les prédictions CSV', export, 'predictions.csv',
                       'text/csv', on_click='ignore')
