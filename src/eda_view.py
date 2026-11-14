"""Vue EDA intégrable : toutes les sorties utilisent le même sous-ensemble filtré."""
import pandas as pd
import matplotlib.pyplot as plt
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

def render_eda(df):
    st.title('Explorer les observations d’incendie')
    st.caption('Entraînement 2012-2023. Les proportions décrivent cet échantillon sélectionné.')
    training = df.loc[df['split'].eq('train')]
    if training.empty:
        st.info('Aucune donnée d’entraînement disponible.')
        return
    first, last = int(training.year.min()), int(training.year.max())
    if first == last:
        bounds = (first, last)
    else:
        bounds = st.slider('Années', first, last, (first, last), key='eda_years')
    labels = st.multiselect('Classes', [0, 1], default=[0, 1],
                            format_func=lambda x: 'Avec détection' if x else 'Sans détection', key='eda_labels')
    months_available = sorted(pd.to_datetime(training['date']).dt.month.unique().tolist())
    months = st.multiselect('Mois', months_available, default=months_available, key='eda_months')
    cells = st.multiselect('Zones (vide = toutes)', sorted(training['cell_id'].unique().tolist()),
                           default=[], key='eda_cells')
    filtered = filter_training(df, bounds, labels, months=months, cells=cells)
    if filtered.empty:
        st.info('Aucune observation ne correspond aux filtres.')
        return
    a, b, c = st.columns(3)
    a.metric('Observations', f'{len(filtered):,}')
    b.metric('Zones', f'{filtered.cell_id.nunique():,}')
    c.metric('Part étiquetée 1', f'{filtered.label.mean():.1%}')
    excluded = {'label', 'year', 'doy', 'lat', 'lon', 'cell_id', 'n_detections', 'max_frp',
                'days_since_last_fire', 'ndvi_normal', 'ndvi_anomaly'}
    numeric = [col for col in filtered.select_dtypes('number').columns
               if col not in excluded and not col.startswith('Unnamed:')]
    if not numeric:
        st.info('Aucune variable numérique exploitable dans ce fichier.')
        return
    if 'days_since_last_fire' in filtered:
        sentinel_count = int(filtered['days_since_last_fire'].eq(9999).sum())
        st.caption(f'Code spécial 9999 : {sentinel_count:,} lignes du filtre. '
                   'Ce code n’est pas une durée mesurée. days_since_last_fire, ndvi_normal '
                   'et ndvi_anomaly restent hors des graphiques de sélection des variables, '
                   'en attendant la vérification de leur calcul historique.')
    st.subheader('1. Statistiques descriptives')
    st.dataframe(filtered[numeric].describe().T)
    st.caption('count = valeurs présentes ; std = dispersion ; 50% = médiane. '
               'Les valeurs extrêmes ne sont pas supprimées automatiquement.')
    st.subheader('2. Valeurs manquantes')
    missing = pd.DataFrame({'nombre': filtered.isna().sum(), 'pourcentage': filtered.isna().mean() * 100})
    st.dataframe(missing)
    fig, ax = plt.subplots(figsize=(9, 4))
    nonzero = missing.loc[missing['nombre'].gt(0), 'pourcentage']
    if nonzero.empty:
        ax.text(0.5, 0.5, 'Aucune valeur manquante dans ce filtre', ha='center', va='center')
        ax.set_axis_off()
    else:
        nonzero.plot.barh(ax=ax, color='#0891b2')
        ax.set_xlabel('Valeurs manquantes (%)')
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('Une valeur absente n’est pas un zéro. Son remplacement pour les modèles '
               'est appris uniquement dans les données d’entraînement de chaque pli.')
    st.subheader('3. Histogramme et densité KDE')
    column = st.selectbox('Variable numérique', numeric, key='eda_variable')
    subset = filtered[column].dropna()
    subset = subset.sample(n=min(5000, len(subset)), random_state=42)
    st.caption('Graphique sur au plus 5 000 valeurs non manquantes du filtre. Statistiques sur toutes les lignes filtrées.')
    if subset.empty:
        st.info('Variable entièrement manquante pour ce filtre.')
    else:
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.histplot(subset, bins=30, stat='density', kde=subset.nunique() > 1, ax=ax, color='#d97706')
        ax.set_title(column)
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('L’histogramme indique où se concentrent les valeurs. La KDE est une '
               'courbe lissée de cette distribution, pas une probabilité d’incendie.')
    st.subheader('Comparaison par classe : boîte à moustaches')
    box_data = filtered[['label', column]].dropna()
    if not box_data.empty:
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.boxplot(data=box_data, x='label', y=column, ax=ax, color='#7dd3fc')
        ax.set_xlabel('Classe : 0 = sans détection ; 1 = avec détection')
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        st.caption('La ligne centrale est la médiane ; la boîte contient les 50 % centraux. '
                   'Les points isolés sont des valeurs éloignées, pas forcément des erreurs. '
                   'Calcul sur toutes les valeurs présentes du filtre.')
    st.subheader('4. Fréquences des catégories')
    category = st.selectbox('Catégorie', ['label', 'mois'], key='eda_category')
    values = filtered['label'] if category == 'label' else pd.to_datetime(filtered['date']).dt.month
    counts = values.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 4))
    counts.plot.bar(ax=ax, color='#64748b')
    ax.set(xlabel=category, ylabel='Effectif')
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('Ces fréquences décrivent les observations sélectionnées dans le fichier, '
               'pas la fréquence réelle des incendies en Algérie.')
    st.subheader('5. Corrélations de Spearman')
    defaults = [v for v in ['temp_max', 'rh_mean', 'wind_mean', 'precip_sum', 'fwi', 'ndvi'] if v in numeric]
    selected = st.multiselect('Variables à comparer', numeric, default=defaults, key='eda_corr')
    if len(selected) < 2:
        st.info('Choisir au moins deux variables.')
    elif len(filtered) < 3:
        st.info('Trop peu de lignes pour afficher une corrélation utile.')
    else:
        corr = filtered[selected].corr(method='spearman')
        if corr.notna().sum().sum() == 0:
            st.info('Corrélations indéfinies : valeurs constantes ou manquantes.')
        else:
            fig, ax = plt.subplots(figsize=(max(7, len(selected) * .55), max(5, len(selected) * .5)))
            sns.heatmap(corr, vmin=-1, vmax=1, center=0, cmap='RdBu_r', ax=ax)
            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption('Une corrélation est une association, pas une preuve de causalité. '
               'Des variables très liées peuvent apporter des informations redondantes.')
    st.caption('6. Les filtres années, classes, mois et zones s’appliquent à tous les tableaux et graphiques.')
