"""Shared identity and accessible page headings."""
from pathlib import Path
import streamlit as st

SECTIONS = {
    'Accueil': ('Command Center', 'Observatoire', 'Suivez les détections d’incendie dans les cellules-jours échantillonnées en Algérie.'),
    'Exploration': ('Data Explorer', 'Entraînement · 2012–2023', 'Isolez une population et examinez ses distributions, ses données manquantes et ses corrélations.'),
    'Carte': ('Geo Intelligence', 'Territoire · Algérie', 'Explorez les cellules géolocalisées et comparez leurs effectifs sur une période.'),
    'Modèles': ('Model Arena', 'Validation 2024 · Test 2025', 'Comparez les modèles sur la validation ou consultez le résultat publié de la décision gelée.'),
    'Prédiction': ('Prediction Studio', 'Classification rétrospective', 'Renseignez les mesures d’une cellule-jour pour interroger un pipeline entraîné.'),
    'Méthodologie': ('Scientific Insights', 'Protocole et résultats', 'Consultez la traçabilité du jeu de données et les comparaisons statistiques appariées.'),
}


def navigation():
    st.html('<style>' + Path(__file__).with_name('atlas.css').read_text() + '</style>')
    st.sidebar.html('<div class="atlas-brand"><i aria-hidden="true"></i>Wildfire <span>Atlas</span></div>')
    icons = dict(zip(SECTIONS, ['space_dashboard', 'query_stats', 'public', 'leaderboard',
                               'tune', 'science']))
    return st.sidebar.radio('Espaces de travail', SECTIONS.keys(), key='page',
                            format_func=lambda key: f":material/{icons[key]}: {SECTIONS[key][0]}")


def heading(page):
    title, scope, description = SECTIONS[page]
    st.html(f'<header class="atlas-heading"><small>{scope}</small><h1>{title}</h1><p>{description}</p></header>')
