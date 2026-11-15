"""Lancement : python -m streamlit run src/siad03_extensions/dashboard.py."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import pandas as pd
import streamlit as st
from src.eda_view import render_eda
from src.siad03_extensions.data import load_development
from src.siad03_extensions.exploration import summarize


@st.cache_data
def training_data():
    train, _, _, _ = load_development()
    train['month'] = train.date.dt.month
    return train


def render_scientific_dashboard():
    st.title('Observatoire scientifique des détections')
    st.caption('Contribution SIAD03 · Classification rétrospective · Test 2025 réservé')
    st.warning('Négatifs sélectionnés : les proportions et probabilités ne représentent pas un risque territorial. Données disponibles de juin à octobre seulement.')
    try:
        train = training_data()
    except (ValueError, OSError) as exc:
        st.error(f'Données indisponibles : {exc}')
        return
    eda, geo, performance = st.tabs(['EDA complète', 'Espace et temps', 'Validation et erreurs'])
    with eda:
        render_eda(train)
    with geo:
        years = st.slider('Période cartographique', 2012, 2023, (2012, 2023), key='science_years')
        months = st.multiselect('Mois observés', [6,7,8,9,10], default=[6,7,8,9,10], key='science_months')
        minimum = st.number_input('Effectif minimum par cellule', min_value=1, value=20, step=1)
        selected = train.loc[train.year.between(*years) & train.month.isin(months)]
        if selected.empty:
            st.info('Aucune observation pour cette sélection.')
        else:
            cells = summarize(selected, ['cell_id']).merge(selected.groupby('cell_id')[['lat','lon']].first(), on='cell_id')
            cells = cells.loc[cells.n >= minimum].copy()
            st.write(f'{len(selected):,} observations sélectionnées ; {len(cells):,} cellules affichables.')
            if cells.empty:
                st.info('Aucune cellule ne satisfait l’effectif minimum.')
            else:
                cells['size'] = 100 + 20*cells.n.pow(.5)
                cells['color'] = cells.sample_fraction.map(lambda p: [int(255*p), 70, int(255*(1-p)), 180])
                st.map(cells, latitude='lat', longitude='lon', size='size', color='color')
                st.caption('Couleur rouge : fraction observée élevée ; taille : effectif. Aucun lissage spatial ni découpage administratif.')
                st.dataframe(cells[['cell_id','n','detections','sample_fraction','lat','lon']], hide_index=True)
                st.download_button('Exporter les cellules filtrées', cells.drop(columns=['color','size']).to_csv(index=False), 'cellules.csv', 'text/csv')
            monthly = summarize(selected, ['year','month'])
            st.dataframe(monthly, hide_index=True)
            st.line_chart(monthly.pivot(index='month', columns='year', values='sample_fraction'))
    with performance:
        folder = ROOT/'results/siad03_extensions/benchmark'
        if not (folder/'metrics.csv').exists():
            st.info('Exécuter le benchmark indépendant pour afficher les résultats.')
        else:
            table = pd.read_csv(folder/'metrics.csv')
            st.caption('Validation 2024, seuil 0,5. Choix des hyperparamètres sur train uniquement. Résultats exploratoires, pas de test final.')
            st.dataframe(table, hide_index=True)
            name = st.selectbox('Modèle', table.model.tolist(), key='science_model')
            group = st.selectbox('Analyse des erreurs', ['month','season','spatial_block','temp_max_bin','rh_mean_bin','precip_sum_bin','seen_cell'])
            st.dataframe(pd.read_csv(folder/f'{name}_errors_{group}.csv'), hide_index=True)
            st.subheader('Calibration descriptive')
            cal = pd.read_csv(folder/f'{name}_calibration.csv')
            st.dataframe(cal, hide_index=True)
            st.line_chart(cal.set_index('predicted')[['observed']])
            st.subheader('Intervalles bootstrap par cellule')
            st.dataframe(pd.read_csv(folder/f'{name}_intervals.csv'), hide_index=True)
            st.caption('300 réplications conditionnelles à 2024. Dépendance entre cellules voisines non corrigée ; pas un intervalle de performance future.')
            st.info('L’artefact historique DecisionTree a été enregistré avec une autre version de scikit-learn : comparaison indicative jusqu’au réentraînement par son responsable.')


if __name__ == '__main__':
    st.set_page_config(page_title='Observatoire SIAD03', layout='wide')
    render_scientific_dashboard()
