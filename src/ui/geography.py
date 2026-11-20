"""Carte agrégée par cellule sur l'entraînement."""
import numpy as np
import pydeck as pdk
import streamlit as st
from src.ui.services import training


def geography():
    st.title('Carte des observations')
    data = training()
    years = st.slider('Période observée', int(data.year.min()), int(data.year.max()),
                      (int(data.year.min()), int(data.year.max())), key='map_years')
    months = sorted(data.date.dt.month.unique().tolist())
    selected = st.multiselect('Mois observés', months, default=months, key='map_months')
    view = data.loc[data.year.between(*years) & data.date.dt.month.isin(selected)]
    if view.empty:
        st.info('Aucune observation sur cette période.')
        return
    cells = view.groupby('cell_id', as_index=False).agg(lat=('lat','first'), lon=('lon','first'),
        observations=('label','size'), positives=('label','sum'))
    cells['negatives'] = cells.observations - cells.positives
    fraction = cells.positives / cells.observations
    cells['part'] = fraction.map('{:.1%}'.format)
    cells['couleur'] = [[int(35 + 215*x), int(175-65*x), int(196-130*x)] for x in fraction]
    cells['rayon'] = 650 + 95*np.sqrt(cells.observations)
    st.caption(f'{len(view):,} observations · {len(cells):,} cellules. Rayon : effectif. Du bleu à l’orange : part croissante de jours avec détection.')
    layer = pdk.Layer('ScatterplotLayer', data=cells, get_position='[lon, lat]',
                      get_fill_color='couleur', get_radius='rayon', radius_min_pixels=3,
                      pickable=True, auto_highlight=True)
    st.pydeck_chart(pdk.Deck(layers=[layer], map_style='road',
        initial_view_state=pdk.ViewState(latitude=float(cells.lat.mean()), longitude=float(cells.lon.mean()), zoom=5),
        tooltip={'text':'Cellule {cell_id}\nAvec détection : {positives}\nSans détection : {negatives}\nPart observée : {part}'}))
    with st.expander('Effectifs par cellule'):
        st.dataframe(cells[['cell_id','lat','lon','observations','positives','negatives','part']], hide_index=True)
