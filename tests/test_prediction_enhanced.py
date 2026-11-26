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
    with pytest.raises(ValueError, match='incomplètes'):
        validate_batch(frame.drop(columns=[features[0]]), features)


def test_reversed_columns_restored(frame, features):
    result = validate_batch(frame[list(reversed(features))], features)
    pd.testing.assert_frame_equal(result, frame.astype(float))


def test_extra_column_rejected(frame, features):
    frame.insert(0, 'cell_id', ['a'] * len(frame))
    with pytest.raises(ValueError, match='inattendues'):
        validate_batch(frame, features)


def test_non_numeric_rejected(frame, features):
    frame[features[0]] = frame[features[0]].astype(str)
    frame.loc[0, features[0]] = 'inconnu'
    with pytest.raises(ValueError, match='numérique'):
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
    with pytest.raises(ValueError, match='renseignée'):
        validate_batch(frame, features)
    out = validate_batch(frame, features, allow_missing=True)
    assert int(out['ndvi'].isna().sum()) == 1


def test_predict_batch_matches_model(frame, features):
    model = pipeline('GaussianNB')
    final = decision()
    threshold = final['threshold'] if final['model'] == 'GaussianNB' else .5
    out = predict_batch(model, frame, threshold)
    proba = model.predict_proba(out[features])[:, list(model.classes_).index(1)]
    assert np.allclose(out['score_classe_1'].to_numpy(), proba)
    assert set(out['classe']) <= {0, 1}
    assert (out['classe'] == (out['score_classe_1'] >= threshold).astype(int)).all()
    assert out['tranche_score'].tolist() == alert_labels(out['score_classe_1'])


def test_predict_batch_refuses_extra_columns(frame, features):
    frame.insert(0, 'cell_id', [f'c{i}' for i in range(len(frame))])
    with pytest.raises(ValueError, match='inattendues'):
        predict_batch(pipeline('GaussianNB'), frame, .5)


def test_predictions_csv_roundtrip(frame, features):
    out = predict_batch(pipeline('GaussianNB'), frame, .5)
    from src.ui.batch import score_batch
    from src.ui.services import input_summary
    export = out.assign(modele='GaussianNB', seuil=.5)
    # Une valeur délibérément obsolète de l’export doit être écartée.
    export['score_classe_1'] = '=FORMULE()'
    export['tranche_score'] = 'inconnue'
    restored = score_batch(export.to_csv(index=False).encode(), pipeline('GaussianNB'), .5,
                           input_summary(tuple(features)))
    np.testing.assert_allclose(restored.score_classe_1, out.score_classe_1)
    pd.testing.assert_series_equal(restored.tranche_score, out.tranche_score)


def test_example_csv_validates(features):
    raw = pd.read_csv(io.BytesIO(example_csv(features)))
    assert list(raw.columns) == features
    validate_batch(raw, features)


def test_advanced_studio_renders_in_studio():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    assert not app.exception and not app.error
    app.radio(key='studio_mode').set_value('Fichier CSV').run()
    assert not app.exception and not app.error
    assert any('Classifier un lot' in item.value for item in app.subheader)
    assert len(app.selectbox) == 1


def test_alert_badge_shown_after_prediction():
    app = AppTest.from_file(str(ROOT/'src/app.py'), default_timeout=60).run()
    app.radio(key='page').set_value('Prédiction').run()
    app.button[0].click().run()
    assert not app.exception and not app.error
    assert any('Tranche du score' in item.value for item in app.markdown)
    assert any('classe 1 est attribuée' in item.value for item in app.caption)
