import io
import numpy as np
import pandas as pd
import pytest
from src.explainability.alert_levels import alert_labels
from src.ui.prediction_enhanced import (example_csv, predict_batch,
                                        protocol_features, validate_batch)
from src.ui.services import ROOT, decision, pipeline, training
from streamlit.testing.v1 import AppTest


@pytest.fixture
def features():
    return protocol_features()


@pytest.fixture
def frame(features):
    return training()[features].dropna().iloc[:5].reset_index(drop=True).copy()


def test_protocol_features_match_protocole(features):
    import json
    from src.ui.services import CONFIG
    assert len(features) == 24
    assert features == json.loads(CONFIG.read_text(encoding='utf-8'))['features']


def test_validate_batch_returns_protocol_order(frame, features):
    out = validate_batch(frame, features)
    assert list(out.columns) == features
    assert len(out) == 5
    assert out.dtypes.map(lambda dtype: dtype.kind in 'fi').all()


def test_missing_column_rejected(frame, features):
    with pytest.raises(ValueError, match='Colonnes manquantes'):
        validate_batch(frame.drop(columns=[features[0]]), features)


def test_wrong_order_rejected(frame, features):
    with pytest.raises(ValueError, match='position 1'):
        validate_batch(frame[list(reversed(features))], features)


def test_extra_column_allowed_and_ignored(frame, features):
    frame.insert(0, 'cell_id', ['a'] * len(frame))
    out = validate_batch(frame, features)
    assert list(out.columns) == features


def test_non_numeric_rejected(frame, features):
    frame[features[0]] = frame[features[0]].astype(str)
    frame.loc[0, features[0]] = 'inconnu'
    with pytest.raises(ValueError, match='non numérique'):
        validate_batch(frame, features)


def test_infinity_rejected(frame, features):
    frame.loc[0, features[0]] = np.inf
    with pytest.raises(ValueError, match='infinies'):
        validate_batch(frame, features)


def test_incoherent_measure_rejected(frame, features):
    frame.loc[0, 'rh_mean'] = 150
    with pytest.raises(ValueError, match='incohérentes'):
        validate_batch(frame, features)


def test_fractional_doy_rejected(frame, features):
    frame['doy'] = frame['doy'].astype(float)
    frame.loc[0, 'doy'] = 10.5
    with pytest.raises(ValueError, match='entier'):
        validate_batch(frame, features)


def test_doy_out_of_range_rejected(frame, features):
    frame.loc[0, 'doy'] = 400
    with pytest.raises(ValueError, match='1 et 366'):
        validate_batch(frame, features)


def test_empty_frame_rejected(features):
    with pytest.raises(ValueError, match='aucune observation'):
        validate_batch(pd.DataFrame(columns=features), features)


def test_missing_values_allowed_for_imputation(frame, features):
    frame.loc[0, 'ndvi'] = np.nan
    out = validate_batch(frame, features)
    assert int(out['ndvi'].isna().sum()) == 1


def test_predict_batch_matches_model(frame, features):
    model = pipeline('GaussianNB')
    final = decision()
    threshold = final['threshold'] if final['model'] == 'GaussianNB' else .5
    out = predict_batch(model, frame, threshold)
    proba = model.predict_proba(out[features])[:, list(model.classes_).index(1)]
    assert np.allclose(out['score'].to_numpy(), proba)
    assert set(out['prediction']) <= {0, 1}
    assert (out['prediction'] == (out['score'] >= threshold).astype(int)).all()
    assert out['alerte'].tolist() == alert_labels(out['score'])


def test_predict_batch_keeps_extra_columns(frame, features):
    frame.insert(0, 'cell_id', [f'c{i}' for i in range(len(frame))])
    out = predict_batch(pipeline('GaussianNB'), frame, .5)
    assert 'cell_id' in out.columns
    assert {'score', 'prediction', 'alerte'} <= set(out.columns)


def test_predictions_csv_roundtrip(frame, features):
    out = predict_batch(pipeline('GaussianNB'), frame, .5)
    reloaded = pd.read_csv(io.BytesIO(out.to_csv(index=False).encode('utf-8')))
    assert len(reloaded) == len(out)
    assert {'score', 'prediction', 'alerte'} <= set(reloaded.columns)
    assert np.allclose(reloaded['score'], out['score'])


def test_example_csv_validates(features):
    raw = pd.read_csv(io.BytesIO(example_csv(features)))
    assert list(raw.columns) == features
    validate_batch(raw, features)


def test_advanced_studio_renders_in_studio():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    assert not app.exception and not app.error
    assert any('Studio avancé' in item.value for item in app.subheader)
    assert any('Aucun fichier chargé' in item.value for item in app.caption)


def test_alert_badge_shown_after_prediction():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    app.button[0].click().run()
    assert not app.exception and not app.error
    assert any('Niveau d’alerte' in item.value for item in app.markdown)
    assert any('seuils du protocole' in item.value for item in app.caption)
