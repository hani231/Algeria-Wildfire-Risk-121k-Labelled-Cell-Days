"""Comparer les résultats puis interroger les pipelines entraînés."""
import json
import pandas as pd
import streamlit as st
from src.explainability.alert_levels import alert_badge, alert_level
from src.ui.curves import curves
from src.ui.prediction_enhanced import advanced_studio
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
    view = st.radio('Évaluation à consulter', ['Comparaison 2024', 'Test final 2025'],
                    horizontal=True, key='arena_cohort')
    if view == 'Test final 2025':
        published_result()
        return
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


def published_result():
    result = json.loads((ROOT/'results/test_final/result.json').read_text())
    frozen = decision()
    if (result['model'], result['threshold']) != (frozen['model'], frozen['threshold']):
        raise ValueError('Le résultat publié diffère de la décision gelée.')
    st.subheader(f"{result['model']} · test final au seuil {result['threshold']:.2f}")
    st.caption(f"{result['n']:,} cellules-jours en 2025 · choix gelé dans {result['freeze_commit'][:7]}")
    for col, key, title in zip(st.columns(3), ('precision', 'recall', 'f1'), ('Précision', 'Rappel', 'F1')):
        col.metric(title, f"{result[key]:.3f}")
    detected, alerts = st.columns(2)
    with detected.container(border=True):
        st.subheader('Détections retrouvées')
        st.progress(result['recall'])
        st.write(f"{result['tp']:,} retrouvées sur {result['positives']:,} jours positifs. "
                 f"{result['fn']:,} détections ont été manquées.")
    with alerts.container(border=True):
        st.subheader('Alertes émises')
        st.progress(result['precision'])
        st.write(f"{result['tp']:,} alertes correctes sur {result['tp']+result['fp']:,}. "
                 f"{result['fp']:,} faux positifs dans cet échantillon.")
    st.caption('Résultat publié après la sélection sur 2024. Le seuil et le modèle restent fixes.')
    st.dataframe(pd.DataFrame([{'Accuracy': result['accuracy'], 'Accuracy équilibrée': result['balanced_accuracy'],
                                'ROC-AUC': result['roc_auc'], 'Average Precision': result['average_precision']}]),
                 hide_index=True, width='stretch')


def prediction():
    st.write('Choisissez un modèle puis ajustez les mesures d’une observation. Les valeurs initiales proviennent du premier jour du jeu d’entraînement disponible avec tous les prédicteurs.')
    names = [name for name, path in ARTIFACTS.items() if path.is_file()]
    if not names:
        st.warning('Aucun pipeline compatible disponible.')
        return
    name = st.selectbox('Pipeline', names, key='studio_model')
    final = decision()
    threshold = final['threshold'] if final['model'] == name else .5
    st.caption(f"Seuil appliqué à cette observation : {threshold:.2f}. "
               "Le comparatif des modèles sur 2024 utilise 0,50 pour tous.")
    model = pipeline(name)
    features = list(model.feature_names_in_)
    summary = input_summary(tuple(features))
    settings, result = st.columns([1.7, 1])
    with settings.container():
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
                    values[key] = columns[i % 2].number_input(measure_label(key), key='studio_input_'+key, **params)
        submitted = st.button('Prédire', type='primary', icon=':material/play_arrow:')
    st.divider()
    st.subheader('Studio avancé · import CSV et export')
    advanced_studio()
    with result.container(border=True):
        st.subheader('Lecture du résultat')
        signature = (name, threshold, tuple(values.items()))
        if submitted:
            try:
                label, score = classify(model, values, threshold)
            except ValueError as error:
                st.session_state.pop('last_prediction', None)
                st.error(str(error))
                return
            st.session_state.last_prediction = (signature, label, score)
        saved = st.session_state.get('last_prediction')
        if saved is None or saved[0] != signature:
            message = ('Les mesures ou le modèle ont changé. Relancez la classification.'
                       if saved else 'Ajustez les mesures puis lancez la classification.')
            st.info(message)
            return
        _, label, score = saved
        st.caption(f'{name} · {len(features)} mesures · seuil {threshold:.2f}')
        st.metric('Classe estimée', '1 · Avec détection' if label else '0 · Sans détection')
        if score is not None:
            st.progress(score, text=f'Probabilité du modèle · classe 1 · {score:.1%}')
            level = alert_level(score)
            st.markdown(alert_badge(score), unsafe_allow_html=True)
            st.caption(f'Position sur les seuils du protocole : {level.description}.')
        st.caption('Le score estime la classe d’une cellule-jour dans cet échantillon. Les jours sans détection ont été sélectionnés et la météo inclut la journée observée. Un score de classe ne donne donc pas le risque futur sur le territoire.')
        with st.expander('Mesures utilisées'):
            st.table(pd.Series(values, name='Valeur'))
