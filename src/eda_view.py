"""Vue EDA intégrable : tous les panneaux partagent l'entraînement filtré."""

from src.ui.units import measure_label
import altair as alt
import pandas as pd
import streamlit as st


def filter_training(df, year_bounds, labels, months=None, cells=None):
    mask = (df['split'].eq('train') & df['year'].between(*year_bounds)
            & df['label'].isin(labels))
    if months is not None:
        mask &= pd.to_datetime(df['date']).dt.month.isin(months)
    if cells:
        mask &= df['cell_id'].isin(cells)
    return df.loc[mask].copy()


def _plot_missing(filtered):
    missing = pd.DataFrame({'nombre': filtered.isna().sum(),
                            'pourcentage': filtered.isna().mean() * 100})
    st.dataframe(missing, width='stretch')
    nonzero = missing.loc[missing['nombre'].gt(0), 'pourcentage']
    if nonzero.empty:
        st.info('Aucune valeur manquante dans ce filtre.')
    else:
        st.bar_chart(nonzero.sort_values(), horizontal=True, color='#22D3EE')
    st.caption('Une valeur manquante n’est pas un zéro. Pour les modèles, '
               'son remplacement est appris dans chaque pli d’entraînement.')


def _plot_distributions(filtered, numeric):
    variable = st.selectbox('Variable numérique', numeric, key='eda_variable')
    values = filtered[variable].dropna()
    sample = values.sample(n=min(5000, len(values)), random_state=42)
    if sample.empty:
        st.info('Variable entièrement manquante pour ce filtre.')
    else:
        sample_frame = sample.rename('mesure').to_frame()
        base = alt.Chart(sample_frame)
        hist = base.mark_bar(color='#7765F5').encode(
            x=alt.X('mesure:Q', bin=alt.Bin(maxbins=30), title=measure_label(variable)),
            y=alt.Y('count():Q', title='Effectif'),
            tooltip=[alt.Tooltip('count():Q', title='Observations')])
        if sample.nunique() > 1:
            density = base.transform_density('mesure', as_=['mesure', 'densité']).mark_line(
                color='#22D3EE').encode(x='mesure:Q', y=alt.Y('densité:Q', title='Densité KDE'))
            hist = (hist + density).resolve_scale(y='independent')
        st.altair_chart(hist.properties(height=250), width='stretch')
    st.caption(f'{measure_label(variable)} · {len(sample):,} valeurs tracées sur {len(values):,} présentes. La KDE décrit la '
               'distribution des mesures, pas une probabilité d’incendie.')
    box_data = filtered[['label', variable]].dropna()
    if not box_data.empty:
        quantiles = box_data.groupby('label')[variable].quantile([0, .25, .5, .75, 1]).unstack()
        quantiles.columns = ['min','q1','médiane','q3','max']
        base = alt.Chart(quantiles.reset_index()).encode(y=alt.Y('label:N', title='Classe'),
                                                         tooltip=list(quantiles.columns))
        chart = (base.mark_rule(color='#95a4c5').encode(x='min:Q', x2='max:Q')
                 + base.mark_bar(size=22, color='#7765F5').encode(x='q1:Q', x2='q3:Q')
                 + base.mark_tick(color='white', size=24).encode(x='médiane:Q'))
        st.altair_chart(chart, width='stretch')
    st.caption('La boîte compare toutes les valeurs présentes du filtre. '
               'La ligne couvre le minimum et le maximum, la boîte les quartiles.')


def render_eda(df, standalone=True):
    if standalone:
        st.title('Exploration des détections d’incendie')
    st.caption('Cellules-jours de l’entraînement 2012–2023 · Étude rétrospective')
    training = df.loc[df['split'].eq('train')]
    if training.empty:
        st.info('Aucune donnée d’entraînement disponible.')
        return

    first, last = int(training.year.min()), int(training.year.max())
    with st.sidebar:
        st.header('Filtres EDA')
        st.caption('Tous les panneaux utilisent cette même sélection.')
        bounds = ((first, last) if first == last else
                  st.slider('Années', first, last, (first, last), key='eda_years'))
        labels = st.multiselect('Classes', [0, 1], default=[0, 1],
                                format_func=lambda x: 'Avec détection' if x else 'Sans détection',
                                key='eda_labels')
        available = sorted(pd.to_datetime(training['date']).dt.month.unique().tolist())
        months = st.multiselect('Mois', available, default=available, key='eda_months')
        cells = st.multiselect('Zones (vide = toutes)',
                               sorted(training['cell_id'].unique().tolist()),
                               default=[], key='eda_cells')
    filtered = filter_training(df, bounds, labels, months=months, cells=cells)
    if filtered.empty:
        st.info('Aucune observation ne correspond aux filtres. Élargissez la période, '
                'les mois, les classes ou les zones.')
        return

    a, b, c = st.columns(3)
    a.metric('Observations', f'{len(filtered):,}')
    b.metric('Zones', f'{filtered.cell_id.nunique():,}')
    c.metric('Part étiquetée 1', f'{filtered.label.mean():.1%}')
    st.caption('Ces proportions décrivent des observations sélectionnées ; '
               'elles ne mesurent pas le risque d’incendie du territoire.')
    excluded = {'label', 'year', 'doy', 'lat', 'lon', 'cell_id', 'n_detections',
                'max_frp', 'days_since_last_fire', 'ndvi_normal', 'ndvi_anomaly'}
    numeric = [col for col in filtered.select_dtypes('number').columns
               if col not in excluded and not col.startswith('Unnamed:')]
    if not numeric:
        st.info('Aucune variable numérique exploitable dans ce fichier.')
        return

    overview, distributions, relations = st.tabs(
        ['Vue d’ensemble', 'Distributions', 'Relations entre variables'])
    with overview:
        if st.checkbox("Préparer le téléchargement CSV", key="eda_export"):
            st.download_button("Télécharger la sélection", filtered.to_csv(index=False),
                               file_name="observations_train.csv", mime="text/csv", on_click="ignore")
        with st.expander('Observations et évolution temporelle'):
            st.write(f'{len(filtered):,} lignes · {len(filtered.columns)} colonnes')
            st.table(filtered.head(5))
            st.caption('Types des variables')
            st.table(filtered.dtypes.astype(str).rename('Type'))
            annual = filtered.groupby('year').label.agg(['size','sum'])
            st.line_chart(annual.rename(columns={'size':'Observations','sum':'Avec détection'}))
        st.subheader('Statistiques descriptives')
        st.dataframe(filtered[numeric].describe().T, width='stretch')
        st.caption('count = valeurs présentes · 50 % = médiane · std = dispersion.')
        st.subheader('Valeurs manquantes')
        _plot_missing(filtered)
        if 'days_since_last_fire' in filtered:
            count = int(filtered['days_since_last_fire'].eq(9999).sum())
            st.caption(f'Code spécial 9999 : {count:,} observations sélectionnées. '
                       'Il ne représente pas une durée mesurée.')
        st.subheader('Fréquences observées')
        category = st.selectbox('Catégorie', ['label', 'mois'], key='eda_category')
        values = (filtered['label'] if category == 'label' else
                  pd.to_datetime(filtered['date']).dt.month)
        st.bar_chart(values.value_counts().sort_index().rename('Observations'), color='#22D3EE')
    with distributions:
        st.subheader('Histogramme, densité et comparaison par classe')
        _plot_distributions(filtered, numeric)
    with relations:
        st.subheader('Corrélations de Spearman')
        defaults = [v for v in ['temp_max', 'rh_mean', 'wind_mean',
                                'precip_sum', 'fwi', 'ndvi'] if v in numeric]
        selected = st.multiselect('Variables à comparer', numeric, default=defaults,
                                  key='eda_corr')
        if len(selected) < 2:
            st.info('Choisir au moins deux variables.')
        elif len(filtered) < 3:
            st.info('Trop peu de lignes pour afficher une corrélation utile.')
        else:
            corr = filtered[selected].corr(method='spearman')
            if corr.notna().sum().sum() == 0:
                st.info('Corrélations indéfinies : valeurs constantes ou manquantes.')
            else:
                pairs = corr.rename_axis('Variable').reset_index().melt(
                    id_vars='Variable', var_name='Comparaison', value_name='Coefficient')
                present = filtered[selected].notna().astype('int64')
                shared = (present.T @ present).rename_axis('Variable').reset_index().melt(
                    id_vars='Variable', var_name='Comparaison', value_name='Paires complètes')
                pairs = pairs.merge(shared, on=['Variable', 'Comparaison'])
                heatmap = alt.Chart(pairs).mark_rect().encode(
                    x=alt.X('Variable:N', sort=selected), y=alt.Y('Comparaison:N', sort=selected),
                    color=alt.Color('Coefficient:Q', scale=alt.Scale(domain=[-1, 1], scheme='redblue')),
                    tooltip=['Variable', 'Comparaison', 'Paires complètes:Q', alt.Tooltip('Coefficient:Q', format='.3f')])
                st.altair_chart(heatmap, width='stretch')
        st.caption('Une corrélation décrit une association, sans démontrer une cause.')
