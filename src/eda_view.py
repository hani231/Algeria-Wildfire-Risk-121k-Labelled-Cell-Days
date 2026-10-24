"""Vue EDA intégrable : toutes les sorties utilisent le même sous-ensemble filtré."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def filter_training(df, year_bounds, labels):
    return df.loc[df['split'].eq('train') & df['year'].between(*year_bounds)
                  & df['label'].isin(labels)].copy()

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
    filtered = filter_training(df, bounds, labels)
    if filtered.empty:
        st.info('Aucune observation ne correspond aux filtres.')
        return
    a, b, c = st.columns(3)
    a.metric('Observations', f'{len(filtered):,}')
    b.metric('Zones', f'{filtered.cell_id.nunique():,}')
    c.metric('Part étiquetée 1', f'{filtered.label.mean():.1%}')
    excluded = {'label', 'year', 'doy', 'lat', 'lon', 'n_detections', 'max_frp'}
    numeric = [col for col in filtered.select_dtypes('number').columns
               if col not in excluded and not col.startswith('Unnamed:')]
    st.subheader('1. Statistiques descriptives')
    st.dataframe(filtered[numeric].describe().T)
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
    st.subheader('4. Fréquences des catégories')
    category = st.selectbox('Catégorie', ['label', 'mois'], key='eda_category')
    values = filtered['label'] if category == 'label' else pd.to_datetime(filtered['date']).dt.month
    counts = values.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 4))
    counts.plot.bar(ax=ax, color='#64748b')
    ax.set(xlabel=category, ylabel='Effectif')
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
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
    st.caption('6. Les filtres années et classes en haut de page s’appliquent à tous les tableaux et graphiques.')
