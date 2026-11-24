"""Page Explicabilité : SHAP global sur la validation et waterfall individuel."""
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import shap
from src.explainability.alert_levels import alert_badge
from src.explainability.shap_backend import make_explainer, sample_background
from src.models import CONFIG
from src.siad03_extensions.data import load_development
from src.ui.services import ARTIFACTS, pipeline, training


def _summary_plot(values, frame, kind):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='The NumPy global RNG was seeded',
                                category=FutureWarning)
        shap.summary_plot(values, frame, plot_type=kind, show=False)


@st.cache_data(show_spinner='Chargement des observations de validation…')
def validation():
    return load_development(protocol=CONFIG)[1]


@st.cache_resource(show_spinner='Préparation de l’explicateur SHAP…')
def get_explainer(name):
    model = pipeline(name)
    background = sample_background(training(), list(model.feature_names_in_))
    return make_explainer(model, background)


@st.cache_data(show_spinner='Calcul des contributions SHAP…')
def shap_summary(name, n_rows, seed=42):
    explainer = get_explainer(name)
    features = explainer.features
    complete = validation()[features].dropna()
    sample = complete.sample(n=min(n_rows, len(complete)), random_state=seed)
    explanation = explainer(sample)
    return {'values': np.asarray(explanation.values, dtype=float),
            'base': np.asarray(explanation.base_values, dtype=float),
            'data': np.asarray(explanation.data, dtype=float),
            'features': features, 'strategy': explainer.strategy,
            'background': explainer.background_size}


@st.cache_data(show_spinner='Calcul des contributions de l’observation…')
def shap_row(name, items):
    explainer = get_explainer(name)
    frame = pd.DataFrame([dict(items)])[explainer.features]
    explanation = explainer(frame)
    return {'values': np.asarray(explanation.values, dtype=float).reshape(-1),
            'base': float(np.asarray(explanation.base_values, dtype=float).reshape(-1)[0]),
            'features': explainer.features, 'strategy': explainer.strategy}


def explainability():
    st.write('Les contributions SHAP décomposent le score d’un modèle entre ses variables. '
             'Le total est exact : base + contributions = score. L’interprétation reste '
             'rétrospective et ne décrit pas un risque futur.')
    names = [name for name, path in ARTIFACTS.items() if path.is_file()]
    if not names:
        st.warning('Aucun pipeline compatible disponible.')
        return
    name = st.selectbox('Pipeline', names, key='shap_model')
    n_rows = st.selectbox('Observations expliquées', (25, 50, 100), index=1, key='shap_rows')
    summary = shap_summary(name, n_rows)
    values, features = summary['values'], summary['features']
    frame = pd.DataFrame(summary['data'], columns=features)
    left, right = st.columns(2)
    with left:
        st.subheader('Beeswarm des contributions')
        plt.close('all')
        _summary_plot(values, frame, 'beeswarm')
        st.pyplot(plt.gcf(), clear_figure=True)
        plt.close('all')
    with right:
        st.subheader('Importance moyenne')
        plt.close('all')
        _summary_plot(values, frame, 'bar')
        st.pyplot(plt.gcf(), clear_figure=True)
        plt.close('all')
    strategy = ('arbre exact sur l’estimateur final' if summary['strategy'] == 'arbre'
                else 'permutation model-agnostic sur predict_proba')
    st.caption(f'Méthode : {strategy} · {n_rows} observations de la validation 2024 · '
               f'fond de {summary["background"]} lignes · contributions additives.')
    st.caption('Une contribution positive pousse vers la classe « avec détection ». '
               'Les variables corrélées partagent le signal : la lecture est descriptive, '
               'pas causale.')
    st.divider()
    st.subheader('Contribution d’une observation')
    saved = st.session_state.get('last_prediction')
    if saved is None:
        st.info('Soumettez une observation dans le Prediction Studio pour afficher son waterfall ici.')
        return
    signature, _, score = saved
    model_name, threshold, items = signature
    try:
        row = shap_row(model_name, tuple(items))
    except ValueError as error:
        st.error(f'Impossible d’expliquer cette observation. {error}')
        return
    values_dict = dict(items)
    observed = np.array([values_dict[key] for key in row['features']], dtype=float)
    explanation = shap.Explanation(values=row['values'], base_values=row['base'],
                                   data=observed, feature_names=row['features'])
    plt.close('all')
    shap.plots.waterfall(explanation, max_display=12, show=False)
    st.pyplot(plt.gcf(), clear_figure=True)
    plt.close('all')
    total = float(row['base'] + row['values'].sum())
    st.markdown(alert_badge(score), unsafe_allow_html=True)
    st.caption(f'{model_name} · seuil {threshold:.2f} · base {row["base"]:.4f} + contributions '
               f'= {total:.4f}, score du modèle {score:.4f}. Une variable contribue d’autant '
               'plus qu’elle écarte le score de la base.')
