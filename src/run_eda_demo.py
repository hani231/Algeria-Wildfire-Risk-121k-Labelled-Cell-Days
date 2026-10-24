"""Lancement local : python -m streamlit run src/run_eda_demo.py"""
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.cleaning_guide import clean_data
from src.eda_view import render_eda

@st.cache_data
def load_data(path, modified):
    # modified fait invalider le cache quand le CSV est mis à jour.
    data = pd.read_csv(path)
    return clean_data(data)[0]

st.set_page_config(page_title='Exploration des incendies', layout='wide')
candidates = [ROOT / 'data/processed/dataset_clean.csv', ROOT / 'data/raw/dataset.csv', ROOT / 'Dataset/dataset.csv']
path = next((p for p in candidates if p.exists()), None)
if path is None:
    st.error('Copier dataset.csv dans data/raw/ ou Dataset/, ou exécuter le notebook 01.')
    st.stop()
render_eda(load_data(str(path), path.stat().st_mtime_ns))
