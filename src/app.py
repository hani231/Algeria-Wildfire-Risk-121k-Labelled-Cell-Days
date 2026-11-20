"""Entrée Streamlit du projet collectif."""
from pathlib import Path
import sys
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ui.pages import overview, explore, statistics, methodology
from src.ui.model_pages import models, prediction

st.set_page_config(page_title='Atlas des détections · Algérie', page_icon='🔥', layout='wide')
st.sidebar.title('Atlas des détections')
st.sidebar.caption('ALGÉRIE · CELLULES-JOURS')
pages = {'Accueil': overview, 'Exploration': explore, 'Statistiques': statistics,
         'Modèles': models, 'Prédiction': prediction, 'Méthodologie': methodology}
page = st.sidebar.radio('Navigation', pages.keys(), key='page')
try:
    pages[page]()
except (OSError, ValueError, KeyError) as error:
    st.error(f'Impossible d’afficher le résultat. {error}')
