"""Comparer les résultats puis interroger les pipelines entraînés."""
import pandas as pd
import streamlit as st
from src.ui.curves import curves
from src.ui.services import BENCH, BATCHES, decision, ROOT, ARTIFACTS, comparison, input_summary, pipeline, classify
from src.ui.units import measure_label

DESCRIPTIONS = {
    'K-NN': 'Vote des voisins après imputation et standardisation.',
    'Random Forest': 'Agrège des arbres appris sur des tirages bootstrap.',
    'SVM': 'Sépare les classes par une marge avec noyau. Le score est calibré sur les données d’apprentissage.',
    'Zero-R': 'Prédit la classe majoritaire du train.',
    'GaussianNB': 'Combine les distributions gaussiennes des variables dans chaque classe.',
    'DecisionTree': 'Sépare les observations par une suite de seuils.',
    'LogisticRegression': 'Combine les variables par une somme pondérée.',
    'HistGradientBoosting': 'Additionne les corrections successives de petits arbres.',
}


def models():
    st.caption('Validation 2024 · Seuil de décision 0,5 · F1 de la classe avec détection')
    table = comparison()
    metrics = ['accuracy','precision','recall','f1','balanced_accuracy','roc_auc','average_precision']
    ranking, profile = st.columns([1.4, 1])
    with ranking:
        st.subheader('Classement des modèles')
        metric = st.selectbox('Comparer par', metrics, index=3)
        ordered = table.sort_values(metric, ascending=False)
        st.dataframe(ordered[[metric]], column_config={
            metric: st.column_config.ProgressColumn(metric, min_value=0, max_value=1, format='%.3f')
        }, width='stretch')
    with profile:
        st.subheader('En tête du classement')
        leaders = ordered.index[ordered[metric].eq(ordered[metric].max())]
        st.metric(', '.join(leaders), f'{ordered[metric].max():.3f}')
        st.caption('Le rappel mesure la part de détections retrouvées. La précision mesure la part d’alertes correctes. AP résume la courbe précision-rappel.')
    with st.expander('Disponibilité et origine des résultats', expanded=True):
        rows = []
        mandatory = ('Zero-R', 'K-NN', 'DecisionTree', 'Random Forest', 'GaussianNB', 'SVM')
        for candidate in dict.fromkeys([*mandatory, *table.index]):
            status = 'En attente'
            source = '—'
            if candidate in table.index:
                batch = BATCHES[candidate]
                source = str((batch/'metrics.csv').relative_to(ROOT))
                if candidate in ARTIFACTS and ARTIFACTS[candidate].is_file():
                    status = 'Résultats et artefact disponibles'
                else:
                    status = 'Scores disponibles · pipeline absent'
            rows.append({'Classifieur': candidate,
                         'Catégorie': 'Obligatoire' if candidate in mandatory else 'Supplémentaire',
                         'Disponibilité': status, 'Lot de validation': source})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
    with st.expander('Table complète des métriques'):
        st.dataframe(table[metrics].round(3), width='stretch')
    st.divider()
    name = st.selectbox('Inspecter un modèle', table.index)
    st.write(DESCRIPTIONS[name])
    if name == 'GaussianNB':
        legacy = pd.read_csv(BENCH/'metrics.csv').set_index('model').loc[name]
        st.caption(f"Benchmark commun · F1 = {table.loc[name, 'f1']:.6f} (14 réglages). "
                   f"Expérience historique · F1 = {legacy.f1:.6f} (7 réglages). "
                   "Le classement utilise le lot reproductible sélectionné sur les plis d’entraînement.")
    row = table.loc[name]
    matrix = pd.DataFrame([[row.tn,row.fp],[row.fn,row.tp]], dtype=int,
                          index=['Réel 0','Réel 1'], columns=['Prédit 0','Prédit 1'])
    st.table(matrix)
    st.caption(f'{int(row.fp):,} faux positifs : une détection annoncée sur un jour étiqueté 0. '
               f'{int(row.fn):,} faux négatifs : une détection manquée. '
               'Un rappel élevé réduit la part de détections manquées. Le F1 ignore les coûts opérationnels.')
    if name == 'Zero-R':
        st.write('La classe majoritaire est 0. Prédire toujours 0 donne une accuracy élevée '
                 'sur cet échantillon déséquilibré et un rappel nul pour les détections.')
    curves(name)
    if ARTIFACTS[name].is_file():
        model = pipeline(name)
        estimator = model.steps[-1][1] if hasattr(model,'steps') else model
        with st.expander('Hyperparamètres utilisés'):
            st.json(estimator.get_params(deep=False), expanded=False)
        if hasattr(estimator, 'coef_'):
            st.bar_chart(pd.Series(estimator.coef_[0], index=model.feature_names_in_).rename('Coefficient standardisé'), horizontal=True)
    final = decision()
    st.caption(f"Décision gelée sur 2024 : {final['model']}, seuil {final['threshold']:.2f}. "
               "Les matrices comparatives affichées ci-dessus utilisent toutes le seuil 0,50.")


def prediction():
    st.write('Choisissez un modèle puis ajustez les mesures d’une observation. Les valeurs initiales proviennent du premier jour du jeu d’entraînement disponible avec tous les prédicteurs.')
    names = [name for name, path in ARTIFACTS.items() if path.is_file()]
    if not names:
        st.warning('Aucun pipeline compatible disponible.')
        return
    name = st.selectbox('Pipeline', names)
    model = pipeline(name)
    features = list(model.feature_names_in_)
    summary = input_summary(tuple(features))
    settings, result = st.columns([1.7, 1])
    with settings.form('predict'):
        st.subheader('Mesures de la cellule-jour')
        values = {}
        groups = {'Météo du jour': features[:9], 'Historique météo': features[9:14],
                  'Indices de feu': features[14:20], 'Végétation et saison': features[20:]}
        for title, keys in groups.items():
            with st.expander(title, expanded=title == 'Météo du jour'):
                columns = st.columns(2)
                for i, key in enumerate(keys):
                    limits = summary.loc[key]
                    params = dict(min_value=float(limits.minimum), max_value=float(limits.maximum),
                                  value=float(limits.initial), format='%.4f')
                    if key in ('doy','ndvi_stale_days','days_since_rain_1mm'):
                        params = dict(min_value=int(limits.minimum), max_value=int(limits.maximum),
                                      value=int(limits.initial), step=1)
                    values[key] = columns[i % 2].number_input(measure_label(key), **params)
        submitted = st.form_submit_button('Prédire', type='primary')
    with result.container(border=True):
        st.subheader('Lecture du résultat')
        if not submitted:
            st.caption(f'{name} · {len(features)} variables')
            st.info('Ajustez les mesures puis lancez la classification.')
            return
        try:
            final = decision()
            threshold = final['threshold'] if final['model'] == name else .5
            label, score = classify(model, values, threshold)
            st.caption(f'Seuil de classification : {threshold:.2f}')
        except ValueError as error:
            st.error(str(error))
            return
        st.metric('Classe estimée', '1 · Avec détection' if label else '0 · Sans détection')
        if score is not None:
            st.progress(score, text=f'Probabilité du modèle · classe 1 · {score:.1%}')
        st.caption('Classification rétrospective. La calibration et l’échantillonnage limitent son interprétation comme risque territorial.')
        with st.expander('Mesures utilisées'):
            st.table(pd.Series(values, name='Valeur'))
