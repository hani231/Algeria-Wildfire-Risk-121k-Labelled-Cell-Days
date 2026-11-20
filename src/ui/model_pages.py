"""Comparer les résultats puis interroger les pipelines entraînés."""
import pandas as pd
import streamlit as st
from src.ui.curves import curves
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
    st.metric(f'Meilleur score sur 2024 · {metric}', f'{table[metric].max():.3f}',
              help=', '.join(table.index[table[metric].eq(table[metric].max())]))
    st.write('En tête : ' + ', '.join(table.index[table[metric].eq(table[metric].max())]))
    st.caption('Le rappel mesure la part de détections retrouvées. La précision mesure la part d’alertes correctes. AP résume la courbe précision-rappel.')
    st.bar_chart(table[[metric]], horizontal=True, color='#c45a31')
    st.dataframe(table[metrics].round(3), width='stretch')
    name = st.selectbox('Fiche modèle', table.index)
    st.write(DESCRIPTIONS[name])
    row = table.loc[name]
    matrix = pd.DataFrame([[row.tn,row.fp],[row.fn,row.tp]], dtype=int,
                          index=['Réel 0','Réel 1'], columns=['Prédit 0','Prédit 1'])
    st.table(matrix)
    curves(name)
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
        values = {}
        groups = {'Météo du jour': features[:9], 'Historique météo': features[9:14],
                  'Indices de feu': features[14:20], 'Végétation et saison': features[20:]}
        for title, keys in groups.items():
            with st.expander(title, expanded=title == 'Météo du jour'):
                columns = st.columns(2)
                for i, key in enumerate(keys):
                    series = data[key]
                    params = dict(min_value=float(series.min()), max_value=float(series.max()),
                                  value=float(example[key]), format='%.4f')
                    if key in ('doy','ndvi_stale_days','days_since_rain_1mm'):
                        params = dict(min_value=int(series.min()), max_value=int(series.max()),
                                      value=int(example[key]), step=1)
                    values[key] = columns[i % 2].number_input(key, **params)
        submitted = st.form_submit_button('Prédire', type='primary')
    if submitted:
        label, score = classify(model, values)
        st.metric('Classe estimée', '1 · Avec détection' if label else '0 · Sans détection', border=True)
        st.write(f'Score de probabilité du modèle pour la classe 1 : {score:.1%}.')
        st.caption('Classification rétrospective. La calibration et l’échantillonnage limitent son interprétation comme risque territorial.')
        with st.expander('Mesures utilisées'):
            st.table(pd.Series(values, name='Valeur'))
