from streamlit.testing.v1 import AppTest
from src.ui.services import ROOT, ARTIFACTS, pipeline, training, decision


def test_navigation_and_real_prediction():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    assert not app.exception and not app.error
    for page in ('Exploration','Carte','Modèles','Méthodologie','Prédiction'):
        app.radio(key='page').set_value(page).run()
        assert not app.exception and not app.error, page
    app.button[0].click().run()
    model = pipeline('GaussianNB')
    sample = training()[list(model.feature_names_in_)].dropna().iloc[:1]
    frozen = decision()
    threshold = frozen['threshold'] if frozen['model'] == 'GaussianNB' else .5
    expected = str(int(model.predict_proba(sample)[0,1] >= threshold))
    assert app.metric[0].value.startswith(expected)


def test_no_predictor(monkeypatch):
    monkeypatch.setattr('src.ui.model_pages.ARTIFACTS', {})
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    assert 'Aucun pipeline' in app.warning[0].value


def test_map_empty_months():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Carte').run()
    app.multiselect(key='map_months').set_value([]).run()
    assert not app.exception
    assert 'Aucune observation' in app.info[0].value


def test_curves_use_matching_validation_scores():
    import numpy as np
    from sklearn.metrics import auc
    from src.ui.services import comparison
    from src.ui.curves import curve_points
    for name, row in comparison().iterrows():
        roc, pr = curve_points(name)
        assert np.isclose(auc(roc.iloc[:, 0], roc.iloc[:, 1]), row.roc_auc)
        assert np.isclose(-np.sum(np.diff(pr.Rappel) * pr.Précision.iloc[:-1]), row.average_precision)


def test_all_deployed_pipelines_in_studio():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    for name, artifact in ARTIFACTS.items():
        if artifact.is_file():
            app.selectbox[0].set_value(name).run()
            app.button[0].click().run()
            model = pipeline(name)
            example = training()[list(model.feature_names_in_)].dropna().iloc[:1]
            assert not app.exception and not app.error
            frozen = decision()
            threshold = frozen['threshold'] if frozen['model'] == name else .5
            expected = int(model.predict_proba(example)[0,1] >= threshold)
            assert app.metric[0].value.startswith(str(expected))


def test_scientific_insights_preserves_monthly_pairing():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Méthodologie').run()
    assert 'Analyses appariées' in [tab.label for tab in app.tabs]
    next(item for item in app.radio if item.label == 'Appariement').set_value('sensibilite_mois').run()
    assert not app.exception and not app.error
    assert any('p ajustée' in item.value for item in app.caption)


def test_svm_threshold_visible_before_submission():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    app.selectbox[0].set_value('SVM').run()
    assert any('0.20' in item.value and '0,50' in item.value for item in app.caption)


def test_studio_retains_inputs_and_hides_obsolete_results():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    app.selectbox(key='studio_model').set_value('SVM').run()
    app.number_input(key='studio_input_doy').set_value(200).run()
    app.button[0].click().run()
    result = app.metric[0].value
    app.radio(key='page').set_value('Accueil').run()
    app.radio(key='page').set_value('Prédiction').run()
    assert app.number_input(key='studio_input_doy').value == 200
    assert app.selectbox(key='studio_model').value == 'SVM'
    assert app.metric[0].value == result
    app.number_input(key='studio_input_doy').set_value(201).run()
    assert not app.metric and 'Relancez' in app.info[0].value
    app.radio(key='page').set_value('Accueil').run()
    app.radio(key='page').set_value('Prédiction').run()
    assert app.number_input(key='studio_input_doy').value == 201
    assert not app.metric


def test_test_cohort_displays_published_metrics_without_inference(monkeypatch):
    import json
    published = json.loads((ROOT/'results/test_final/result.json').read_text())
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Modèles').run()
    def unexpected(*args, **kwargs):
        raise AssertionError('Le panneau de lecture ne charge aucun estimateur')
    monkeypatch.setattr('src.ui.model_pages.pipeline', unexpected)
    app.radio(key='arena_cohort').set_value('Test final 2025').run()
    assert not app.exception and not app.error
    assert [item.value for item in app.metric] == [
        f'{published[key]:.3f}' for key in ('precision', 'recall', 'f1')]
    assert not app.selectbox
