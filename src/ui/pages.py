"""Pages de l'observatoire, alimentées par les résultats versionnés."""
import json
import pandas as pd
import streamlit as st
from src.ui.geography import summarize_cells, territory
from src.eda_view import render_eda
from src.ui.services import ROOT, ARTIFACTS, comparison, training, pipeline, classify


def navigate(page):
    st.session_state['page'] = page


def overview():
    audit = json.loads((ROOT/'results/audit_siad03/qualite.json').read_text())
    spatial, summary = st.columns([2.2, 1])
    with spatial:
        st.subheader('Empreinte des observations')
        territory(summarize_cells(training()), height=310)
        st.button('Ouvrir la carte', on_click=navigate, args=('Carte',))
    with summary:
        st.subheader('Couverture du CSV')
        st.metric('Cellules-jours', f"{audit['lignes_avant']:,}")
        st.metric('Zones échantillonnées', f"{audit['zones']:,}")
        st.caption(f"Du {audit['debut']} au {audit['fin']}. Carte limitée à l’entraînement.")
    annual = pd.read_csv(ROOT/'results/siad03_extensions/exploration/annual.csv').set_index('year')
    annual['Sans détection'] = annual.n - annual.detections
    trend, actions = st.columns([2.2, 1])
    with trend:
        st.subheader('Saisons de détection')
        st.area_chart(annual.rename(columns={'detections':'Avec détection'})[['Avec détection','Sans détection']],
                      color=['#FF654D','#7765F5'], height=220)
        st.caption('Effectifs annuels dans l’échantillon d’entraînement.')
    with actions:
        st.subheader('Classes du train')
        counts = audit['effectifs_train']
        share = counts['1'] / sum(counts.values())
        st.progress(share, text=f"{share:.1%} avec détection")
        st.write(f"{counts['1']:,} avec détection · {counts['0']:,} sans détection")
        st.button('Explorer les observations', on_click=navigate, args=('Exploration',))
        st.button('Classer une observation', on_click=navigate, args=('Prédiction',))


def reset_filters():
    for key in list(st.session_state):
        if key.startswith(('eda_', 'range_')):
            del st.session_state[key]


def explore():
    data = training()
    st.sidebar.button('Réinitialiser les filtres', on_click=reset_filters)
    var = st.sidebar.selectbox('Plage de valeurs', ['Toutes','temp_max','rh_mean','ndvi'], key='range_col')
    if var != 'Toutes':
        present = data[var].dropna()
        if present.nunique() > 1:
            low, high = float(present.min()), float(present.max())
            bounds = st.sidebar.slider(var, low, high, (low, high), key='range_'+var)
            data = data[data[var].between(*bounds)]
    render_eda(data)


def statistics():
    st.subheader('Température et humidité les jours de détection')
    st.write('Dans une même zone et une même année, les jours avec détection sont-ils plus chauds ou plus secs ?')
    suffix = st.radio('Appariement', ['principal','sensibilite_mois'], horizontal=True,
                      format_func=lambda s: 'Zone et année' if s=='principal' else 'Zone, année et mois')
    folder = ROOT/'results/audit_siad03'
    stats = pd.read_csv(folder/f'statistiques_{suffix}.csv').set_index('variable')
    gaps = pd.read_csv(folder/f'ecarts_{suffix}.csv').set_index('annee')
    st.caption('Test exact des signes sur les années. Sous H0, un écart annuel non nul a autant de chances d’être positif que négatif. Correction de Holm pour deux tests.')
    for col, (var, title, unit) in zip(st.columns(2), [('temp_max','Température maximale','unités du CSV'),('rh_mean','Humidité moyenne','points')]):
        row = stats.loc[var]
        col.metric(title, f'{row.ecart_annuel_moyen:+.2f} {unit}', border=True)
        col.line_chart(gaps[[var]])
        col.caption(f'p ajustée = {row.p_holm:.6f} · {int(row.annees_non_nulles)} années à écart non nul')
    st.write('En moyenne, les jours avec détection sont plus chauds et moins humides dans cet échantillon. La dépendance entre saisons limite l’interprétation des tests.')


def methodology():
    st.subheader('Origine des observations')
    st.write('Les observations proviennent du jeu Algeria Wildfire Risk publié sur Kaggle. Les négatifs sélectionnés limitent l’interprétation des proportions à cet échantillon.')
    st.link_button('Source des données', 'https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days')
    st.subheader('Du CSV à la classification')
    st.write('Le nettoyage vérifie les dates et les clés zone/jour, traite les doublons et retire sample_kind, n_detections et max_frp. Les transformations apprises restent dans les pipelines.')
    st.write('Entraînement 2012–2023, cinq plis temporels, validation 2024. Le test 2025 est réservé. La météo du jour sert à une classification rétrospective.')
    audit = json.loads((ROOT/'results/audit_siad03/qualite.json').read_text())
    for column, (split, period) in zip(st.columns(3), [('train','Train · 2012–2023'), ('val','Validation · 2024'), ('test','Réservé · 2025')]):
        column.metric(period, f"{audit['lignes_par_partition'][split]:,}")
    st.subheader('Contrôles de cohérence du CSV')
    st.dataframe(pd.Series(audit['controles_coherence'], name='Anomalies'), width='stretch')
    config = json.loads((ROOT/'results/protocole_propose.json').read_text())
    with st.expander('Variables utilisées par les pipelines'):
        st.write(', '.join(config['features']))
    st.subheader('Contributions')
    st.write('SIAD03 : audit, statistiques, EDA, Zero-R, GaussianNB et interface. Le plan attribue le prétraitement et le protocole au responsable K-NN/SVM, et l’arbre, la forêt et l’assemblage final au responsable intégration.')
    st.link_button('Dépôt de l’équipe', 'https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days')
