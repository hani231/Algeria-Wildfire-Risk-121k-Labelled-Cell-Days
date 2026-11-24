"""Entrée Streamlit du projet collectif."""
from pathlib import Path
import sys
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ui.pages import overview, explore, statistics, methodology
from src.ui.geography import geography
from src.ui.model_pages import models, prediction

from src.ui.shell import heading, navigation

st.set_page_config(page_title='Wildfire Atlas · Algérie', page_icon='🌐', layout='wide')
pages = {'Accueil': overview, 'Exploration': explore, 'Carte': geography,
         'Modèles': models, 'Prédiction': prediction, 'Méthodologie': methodology}
# Conserver les filtres des espaces momentanément démontés par Streamlit.
for key in list(st.session_state):
    if key.startswith(('eda_', 'range_', 'map_', 'studio_')):
        st.session_state[key] = st.session_state[key]
page = navigation()
heading(page)
try:
    if page == 'Méthodologie':
        protocol, analysis = st.tabs(['Protocole et qualité', 'Analyses appariées'])
        with protocol:
            methodology()
        with analysis:
            statistics()
    else:
        pages[page]()
except (OSError, ValueError, KeyError) as error:
    st.error(f'Impossible d’afficher le résultat. {error}')
