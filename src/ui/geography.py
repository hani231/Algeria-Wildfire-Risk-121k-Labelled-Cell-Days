"""Geographic views based on observed coordinates and local Natural Earth boundaries."""
import json
from pathlib import Path

import numpy as np
import pydeck as pdk
import streamlit as st

from src.ui.services import training


def summarize_cells(view):
    cells = view.groupby('cell_id', as_index=False).agg(
        lat=('lat', 'first'), lon=('lon', 'first'),
        observations=('label', 'size'), positives=('label', 'sum'))
    cells['negatives'] = cells.observations - cells.positives
    fraction = cells.positives / cells.observations
    cells['part'] = fraction.map('{:.1%}'.format)
    cells['couleur'] = [[int(34 + 221*x), int(211-110*x), int(238-161*x)] for x in fraction]
    cells['rayon'] = 600 + 100*np.sqrt(cells.observations)
    return cells


def territory(cells, height=400):
    borders = json.loads(Path(__file__).with_name('maghreb.geojson').read_text())
    land = pdk.Layer('GeoJsonLayer', data=borders, filled=True, stroked=True,
                     get_fill_color=[30,42,64], get_line_color=[99,115,149], line_width_min_pixels=1)
    dots = pdk.Layer('ScatterplotLayer', data=cells, get_position='[lon, lat]',
                     get_fill_color='couleur', get_radius='rayon', radius_min_pixels=2,
                     pickable=True, auto_highlight=True)
    st.pydeck_chart(pdk.Deck(layers=[land, dots], map_provider=None, map_style=None,
        views=[pdk.View('MapView', controller=True, clear=True)],
        initial_view_state=pdk.ViewState(latitude=float(cells.lat.median()),
                                        longitude=float(cells.lon.median()), zoom=5),
        tooltip={'text':'{cell_id}\nAvec détection : {positives}\nSans détection : {negatives}\nPart observée : {part}'}),
        height=height)
    st.caption('Cyan → braise : part croissante de détections · Rayon : effectif · Fond : Natural Earth')


def geography():
    data = training()
    controls, spatial = st.columns([1, 2.5])
    with controls:
        st.subheader('Période et couverture')
        first, last = int(data.year.min()), int(data.year.max())
        years = st.slider('Années', first, last, (first, last), key='map_years')
        months = sorted(data.date.dt.month.unique().tolist())
        selected = st.multiselect('Mois observés', months, default=months, key='map_months')
        view = data.loc[data.year.between(*years) & data.date.dt.month.isin(selected)]
        if view.empty:
            st.info('Aucune observation sur cette période.')
            return
        cells = summarize_cells(view)
        st.metric('Cellules couvertes', f'{len(cells):,}')
        st.metric('Jours-cellules avec détection', f'{int(cells.positives.sum()):,}')
    with spatial:
        territory(cells, height=460)
    with st.expander('Consulter les coordonnées et les effectifs'):
        st.dataframe(cells[['cell_id','lat','lon','observations','positives','negatives','part']], hide_index=True)
