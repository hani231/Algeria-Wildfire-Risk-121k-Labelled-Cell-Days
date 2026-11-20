"""Comparer les résultats puis interroger les pipelines entraînés."""
import pandas as pd
import streamlit as st
from src.ui.services import ARTIFACTS, comparison, training, pipeline, classify

DESCRIPTIONS = {
    'Zero-R': 'Prédit la classe majoritaire du train.',
    'GaussianNB': 'Combine les distributions gaussiennes des variables dans chaque classe.',
    'DecisionTree': 'Sépare les observations par une suite de seuils.',
    'LogisticRegression': 'Combine les variables par une somme pondérée.',
    'HistGradientBoosting': 'Additionne les corrections successives de petits arbres.',
}


def models():
    st.title('Comparaison des classifieurs')
    st.caption('Validation 2024 · Seuil de décision 0,5 · F1 de la classe avec détection')
    table = comparison()
    metrics = ['accuracy','precision','recall','f1','roc_auc','average_precision']
    metric = st.selectbox('Comparer par', metrics, index=3)
    st.bar_chart(table[[metric]], horizontal=True, color='#c45a31')
    st.dataframe(table[metrics].round(3), width='stretch')
    name = st.selectbox('Fiche modèle', table.index)
    st.write(DESCRIPTIONS[name])
    row = table.loc[name]
    matrix = pd.DataFrame([[row.tn,row.fp],[row.fn,row.tp]], dtype=int,
                          index=['Réel 0','Réel 1'], columns=['Prédit 0','Prédit 1'])
    st.table(matrix)
    if name == 'DecisionTree':
        st.info('Arbre historique enregistré avec scikit-learn 1.9.1. Réentraînement requis pour la saisie interactive en 1.8.0.')
        search = pd.read_csv(ARTIFACTS['GaussianNB'].parents[2]/'recherche_arbre_decision.csv')
        st.write('Réglage retenu', search.loc[search.mean_test_f1.idxmax(), 'params'])
    elif ARTIFACTS[name].is_file():
        model = pipeline(name)
        estimator = model.steps[-1][1] if hasattr(model,'steps') else model
        with st.expander('Hyperparamètres utilisés'):
            st.json(estimator.get_params(deep=False), expanded=False)
        if hasattr(estimator, 'coef_'):
            st.bar_chart(pd.Series(estimator.coef_[0], index=model.feature_names_in_).rename('Coefficient standardisé'), horizontal=True)
    st.caption('Random Forest, K-NN et SVM : résultats indisponibles.')


def prediction():
    st.title('Classer une cellule-jour')
    st.write('Choisissez un modèle puis ajustez les mesures d’une observation. Les valeurs initiales proviennent du premier jour du jeu d’entraînement disponible avec tous les prédicteurs.')
    names = [name for name, path in ARTIFACTS.items() if path.is_file()]
    if not names:
        st.warning('Aucun pipeline compatible disponible.')
        return
    name = st.selectbox('Pipeline', names)
    model = pipeline(name)
    features = list(model.feature_names_in_)
    data = training()[features]
    example = data.dropna().iloc[0]
    with st.form('predict'):
        columns = st.columns(3)
        values = {}
        for i, key in enumerate(features):
            low, high = float(data[key].min()), float(data[key].max())
            values[key] = columns[i % 3].number_input(key, min_value=low, max_value=high,
                                                      value=float(example[key]), format='%.4f')
        submitted = st.form_submit_button('Prédire', type='primary')
    if submitted:
        label, score = classify(model, values)
        st.metric('Classe estimée', '1 · Avec détection' if label else '0 · Sans détection', border=True)
        st.write(f'Score de probabilité du modèle pour la classe 1 : {score:.1%}.')
        st.caption('Classification rétrospective. La calibration et l’échantillonnage limitent son interprétation comme risque territorial.')
        with st.expander('Mesures utilisées'):
            st.table(pd.Series(values, name='Valeur'))
