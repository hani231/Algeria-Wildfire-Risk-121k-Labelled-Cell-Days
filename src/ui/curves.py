"""Courbes de classement sur les prédictions sauvegardées de validation."""
import altair as alt
import pandas as pd
import streamlit as st
from sklearn.metrics import precision_recall_curve, roc_curve
from src.ui.services import BENCH, NB


@st.cache_data
def curve_points(name):
    source = NB/'predictions_2024.csv' if name in ('Zero-R','GaussianNB') else BENCH/'predictions_validation.csv'
    data = pd.read_csv(source, usecols=['year','label',name])
    if not data.year.eq(2024).all():
        raise ValueError('Année de validation inattendue.')
    fp, tp, _ = roc_curve(data.label, data[name])
    precision, recall, _ = precision_recall_curve(data.label, data[name], drop_intermediate=True)
    return (pd.DataFrame({'Faux positifs (taux)':fp, 'Rappel':tp}),
            pd.DataFrame({'Rappel':recall,'Précision':precision}))


def curves(name):
    for col, points, title in zip(st.columns(2), curve_points(name), ['Courbe ROC','Précision-rappel']):
        x, y = points.columns
        chart = alt.Chart(points.reset_index()).mark_line(color='#F58E51').encode(
            x=alt.X(x, scale=alt.Scale(domain=[0,1])), y=alt.Y(y, scale=alt.Scale(domain=[0,1])),
            order='index:Q', tooltip=[x,y]).properties(title=title)
        col.altair_chart(chart, width='stretch')
