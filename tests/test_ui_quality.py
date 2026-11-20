"""Contrats entre les vues Streamlit, les cohortes et les artefacts versionnés."""
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from streamlit.testing.v1 import AppTest

from src.ui import services
from src.ui.geography import summarize_cells


def app():
    return AppTest.from_file(str(services.ROOT/'src/app.py'), default_timeout=60).run()


def test_eda_persists_across_navigation_and_resets():
    view = app()
    view.radio(key='page').set_value('Exploration').run()
    view.multiselect(key='eda_labels').set_value([1]).run()
    view.radio(key='page').set_value('Carte').run()
    view.radio(key='page').set_value('Exploration').run()
    assert view.metric[0].value == '28,586'
    next(b for b in view.button if b.label == 'Réinitialiser les filtres').click().run()
    assert view.metric[0].value == '104,979'
    assert not view.exception


@pytest.mark.parametrize(('key', 'value'), [
    ('temp_mean', np.inf), ('temp_min', 'chaud'), ('rh_mean', 110),
    ('precip_sum', -1), ('doy', 0), ('ndvi_stale_days', 2.5), ('ndvi', None),
])
def test_invalid_input(key, value):
    model = services.pipeline('GaussianNB')
    values = services.input_summary(tuple(model.feature_names_in_)).initial.to_dict()
    values[key] = value
    with pytest.raises(ValueError):
        services.classify(model, values)


def test_ui_prevents_inconsistent_temperature_and_never_fits(monkeypatch):
    def fail_fit(*args, **kwargs):
        pytest.fail('Entraînement déclenché par une interaction')
    monkeypatch.setattr(Pipeline, 'fit', fail_fit)
    view = app()
    view.radio(key='page').set_value('Prédiction').run()
    field = next(n for n in view.number_input if n.label.startswith('temp_min ('))
    field.set_value(field.max)
    view.button[0].click().run()
    assert view.error and 'incohérentes' in view.error[0].value
    assert not view.exception


def test_incompatible_artifact_is_reported(tmp_path, monkeypatch):
    path = tmp_path/'legacy.joblib'
    joblib.dump({'unexpected': 'schema'}, path)
    monkeypatch.setitem(services.ARTIFACTS, 'GaussianNB', path)
    view = app()
    view.radio(key='page').set_value('Prédiction').run()
    assert 'schéma' in view.error[0].value and not view.exception


def test_geo_counts_and_coordinate_integrity():
    train = services.training()
    assert train.year.between(2012, 2023).all() and train.split.eq('train').all()
    cells = summarize_cells(train)
    assert cells.observations.sum() == len(train)
    assert cells.positives.sum() == train.label.sum()
    assert (cells.negatives + cells.positives).equals(cells.observations)
    broken = train.iloc[:1].assign(lat=91)
    with pytest.raises(ValueError, match='Coordonnées'):
        summarize_cells(broken)


def test_confusion_matrices_come_from_assigned_batches():
    for name, row in services.comparison().iterrows():
        source = (services.NB/'predictions_2024.csv' if name in ('Zero-R', 'GaussianNB')
                  else services.BENCH/'predictions_validation.csv')
        predictions = pd.read_csv(source)
        assert predictions.year.eq(2024).all()
        actual = confusion_matrix(predictions.label, predictions[name].ge(.5)).ravel()
        assert np.array_equal(actual, row[['tn', 'fp', 'fn', 'tp']].values)
