"""Vue EDA intégrable : tous les panneaux partagent l'entraînement filtré."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
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
        fig, ax = plt.subplots(figsize=(8, max(3, len(nonzero) * .38)))
        nonzero.sort_values().plot.barh(ax=ax, color='#0d9488')
        ax.set(xlabel='Valeurs manquantes (%)', ylabel='')
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('Une valeur manquante n’est pas un zéro. Pour les modèles, '
               'son remplacement est appris dans chaque pli d’entraînement.')


def _plot_distributions(filtered, numeric):
    variable = st.selectbox('Variable numérique', numeric, key='eda_variable')
    values = filtered[variable].dropna()
    sample = values.sample(n=min(5000, len(values)), random_state=42)
    if sample.empty:
        st.info('Variable entièrement manquante pour ce filtre.')
    else:
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.histplot(sample, bins=30, stat='density', kde=sample.nunique() > 1,
                     ax=ax, color='#0d9488')
        ax.set(xlabel=variable, ylabel='Densité')
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('Histogramme et KDE sur au plus 5 000 valeurs. La KDE décrit la '
               'distribution des mesures, pas une probabilité d’incendie.')
    box_data = filtered[['label', variable]].dropna()
    if not box_data.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.boxplot(data=box_data, x='label', y=variable, ax=ax, color='#99f6e4')
        ax.set(xlabel='Classe : 0 = sans détection ; 1 = avec détection', ylabel=variable)
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('La boîte compare toutes les valeurs présentes du filtre. '
               'Les points éloignés ne sont pas automatiquement des erreurs.')


def render_eda(df):
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
        fig, ax = plt.subplots(figsize=(8, 3))
        values.value_counts().sort_index().plot.bar(ax=ax, color='#0d9488')
        ax.set(xlabel=category, ylabel='Observations')
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
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
                fig, ax = plt.subplots(figsize=(max(7, len(selected) * .55),
                                                max(5, len(selected) * .5)))
                sns.heatmap(corr, vmin=-1, vmax=1, center=0, cmap='RdBu_r', ax=ax)
                fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        st.caption('Une corrélation décrit une association, sans démontrer une cause.')
