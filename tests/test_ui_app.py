from streamlit.testing.v1 import AppTest
from src.ui.services import ROOT, ARTIFACTS, pipeline, training


def test_navigation_and_real_prediction():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    assert not app.exception and not app.error
    for page in ('Exploration','Carte','Statistiques','Modèles','Méthodologie','Prédiction'):
        app.radio(key='page').set_value(page).run()
        assert not app.exception and not app.error, page
    app.button[0].click().run()
    model = pipeline('GaussianNB')
    sample = training()[list(model.feature_names_in_)].dropna().iloc[:1]
    expected = str(model.predict(sample)[0])
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
