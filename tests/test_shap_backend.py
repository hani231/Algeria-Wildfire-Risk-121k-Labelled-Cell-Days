import json
import numpy as np
import pandas as pd
import pytest
from src.explainability.shap_backend import make_explainer, sample_background
from src.ui.services import CONFIG, ROOT, pipeline, training
from streamlit.testing.v1 import AppTest

ALL_PIPELINES = ('GaussianNB', 'Zero-R', 'DecisionTree', 'Random Forest',
                 'K-NN', 'SVM', 'LogisticRegression', 'HistGradientBoosting')


@pytest.fixture(scope='module')
def features():
    return list(json.loads(CONFIG.read_text(encoding='utf-8'))['features'])


@pytest.fixture(scope='module')
def background(features):
    return sample_background(training(), features, size=20, seed=42)


def test_sample_background_deterministic(features):
    data = training()
    first = sample_background(data, features, size=10, seed=42)
    second = sample_background(data, features, size=10, seed=42)
    pd.testing.assert_frame_equal(first, second)
    assert list(first.columns) == features
    assert not first.isna().any().any()


def test_sample_background_requires_complete_rows():
    with pytest.raises(ValueError, match='complète'):
        sample_background(pd.DataFrame({'a': [np.nan]}), ['a'])


@pytest.mark.parametrize('name,strategy', [
    ('DecisionTree', 'arbre'), ('Random Forest', 'arbre'),
    ('GaussianNB', 'permutation'), ('Zero-R', 'permutation'),
    ('K-NN', 'permutation'), ('SVM', 'permutation'),
    ('LogisticRegression', 'permutation'),
    ('HistGradientBoosting', 'permutation')])
def test_strategy_selection(name, strategy, features, background):
    explainer = make_explainer(pipeline(name), background)
    assert explainer.strategy == strategy
    assert explainer.background_size == 20


@pytest.mark.parametrize('name', ALL_PIPELINES)
def test_explanations_are_additive(name, features, background):
    model = pipeline(name)
    sample = training()[features].dropna().iloc[:8]
    explanation = make_explainer(model, background)(sample)
    values = np.asarray(explanation.values, dtype=float)
    base = np.asarray(explanation.base_values, dtype=float)
    if values.ndim == 3:
        values, base = values[:, :, 1], base[:, 1]
    totals = base + values.sum(axis=1)
    proba = model.predict_proba(sample)[:, list(model.classes_).index(1)]
    assert np.allclose(totals, proba, atol=1e-6), name
    assert values.shape == (len(sample), 24)
    assert explanation.feature_names == features


def test_explainer_never_refits(features, background, monkeypatch):
    model = pipeline('GaussianNB')
    def forbidden(*args, **kwargs):
        raise AssertionError('réentraînement interdit')
    monkeypatch.setattr(model, 'fit', forbidden, raising=False)
    monkeypatch.setattr(model.steps[-1][1], 'fit', forbidden, raising=False)
    sample = training()[features].dropna().iloc[:2]
    explanation = make_explainer(model, background)(sample)
    assert len(explanation.values) == 2


def test_bare_hgb_explained_without_pipeline_steps(features, background):
    model = pipeline('HistGradientBoosting')
    assert not hasattr(model, 'steps')
    sample = training()[features].dropna().iloc[:3]
    explanation = make_explainer(model, background)(sample)
    values = np.asarray(explanation.values, dtype=float)
    base = np.asarray(explanation.base_values, dtype=float).reshape(-1)
    proba = model.predict_proba(sample)[:, 1]
    assert np.allclose(base + values.sum(axis=1), proba, atol=1e-6)


def test_explainability_page_renders():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=120).run()
    app.radio(key='page').set_value('Explicabilité').run()
    assert not app.exception and not app.error
    assert any('Beeswarm' in item.value for item in app.subheader)
    assert any('Importance moyenne' in item.value for item in app.subheader)
    assert any('Soumettez une observation' in item.value for item in app.info)


def test_waterfall_explains_last_studio_prediction():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=120).run()
    app.radio(key='page').set_value('Prédiction').run()
    app.button[0].click().run()
    assert not app.exception and not app.error
    saved = app.session_state['last_prediction']
    assert saved is not None
    app.radio(key='page').set_value('Explicabilité').run()
    assert not app.exception and not app.error
    assert any('score du modèle' in item.value for item in app.caption)
    assert any('Niveau d’alerte' in item.value for item in app.markdown)
