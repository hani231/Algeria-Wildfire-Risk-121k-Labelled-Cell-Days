import numpy as np
import pytest

from src.ui.batch import MAX_BYTES, MAX_ROWS, read_batch, score_batch
from src.ui.services import ARTIFACTS, classify, input_summary, pipeline


@pytest.fixture(scope='module')
def summary():
    return input_summary(tuple(pipeline('SVM').feature_names_in_))


@pytest.mark.parametrize('name', ARTIFACTS)
def test_matches_single_prediction(name, summary):
    model = pipeline(name)
    threshold = .2 if name == 'SVM' else .5
    frame = summary.initial.to_frame().T
    payload = frame[frame.columns[::-1]].to_csv(index=False).encode('utf-8-sig')
    batch = score_batch(payload, model, threshold, summary)
    label, score = classify(model, frame.iloc[0].to_dict(), threshold)
    assert batch.observation.tolist() == [1] and batch.classe.tolist() == [label]
    assert batch.score_classe_1.iloc[0] == pytest.approx(score)


@pytest.mark.parametrize('payload', [b'', b'x,y\n', b'x,x\n1,2', b'x,label\n1,0',
                                     b'x,y\n1,2,3', b'x,y\n"1,2', b'\xff',
                                     b'a' * (MAX_BYTES + 1), b'x,y\n' + b'1,2\n' * (MAX_ROWS + 1)])
def test_invalid_file(payload):
    with pytest.raises(ValueError):
        read_batch(payload, ['x', 'y'])


@pytest.mark.parametrize(('key', 'value'), [('rh_mean', 101), ('doy', 2.5),
                                             ('wind_mean', np.nan), ('ndvi', np.inf),
                                             ('temp_mean', '=1+2')])
def test_invalid_second_observation_stops_inference(summary, key, value, monkeypatch):
    import pandas as pd
    model = pipeline('SVM')
    frame = pd.DataFrame([summary.initial.to_dict()] * 2, dtype=object)
    frame.loc[1, key] = value
    def unexpected(*args):
        pytest.fail('Le modèle a été appelé sur un lot invalide.')
    monkeypatch.setattr(model, 'predict_proba', unexpected)
    with pytest.raises(ValueError):
        score_batch(frame.to_csv(index=False).encode(), model, .2, summary)


def test_batch_preserves_order_and_model_scores(summary):
    from src.ui.services import training
    model = pipeline('SVM')
    rows = training()[list(model.feature_names_in_)].dropna().iloc[:3].iloc[::-1]
    result = score_batch(rows.to_csv(index=False).encode(), model, .2, summary)
    assert result.observation.tolist() == [1, 2, 3]
    np.testing.assert_allclose(result.score_classe_1, model.predict_proba(rows)[:, 1])
    assert result.classe.tolist() == result.score_classe_1.ge(.2).astype(int).tolist()


@pytest.mark.parametrize('extra', ['sample_kind', 'n_detections', 'max_frp', 'label', 'split',
                                    'score', 'prediction', 'alerte', 'classe', 'tranche_score'])
def test_rejects_leakage_and_partial_export_columns(extra, summary):
    row = summary.initial.to_frame().T.assign(**{extra: '=FORMULE()'})
    with pytest.raises(ValueError, match='En-tête incorrect'):
        score_batch(row.to_csv(index=False).encode(), pipeline('SVM'), .2, summary)


@pytest.mark.parametrize('name', ARTIFACTS)
def test_opt_in_missing_measure_matches_saved_model(name, summary):
    model = pipeline(name)
    row = summary.initial.to_frame().T.copy()
    row['ndvi'] = np.nan
    result = score_batch(row.to_csv(index=False).encode(), model, .2, summary, allow_missing=True)
    assert result.score_classe_1.iloc[0] == pytest.approx(model.predict_proba(row)[0, 1])


def test_rejects_entirely_missing_observation(summary):
    row = summary.initial.to_frame().T.copy()
    row.iloc[:, :] = np.nan
    with pytest.raises(ValueError, match='entière'):
        score_batch(row.to_csv(index=False).encode(), pipeline('SVM'), .2, summary, allow_missing=True)


@pytest.mark.parametrize('metadata', [
    {'score': '=1+2', 'prediction': 100, 'alerte': 'ancienne'},
    {'observation': 900, 'classe': 10, 'score_classe_1': '=1+2', 'modele': 'ancien', 'seuil': -100},
])
def test_reimport_legacy_export_recomputes_only_from_measurements(summary, metadata):
    row = summary.initial.to_frame().T
    model = pipeline('SVM')
    export = row.assign(**metadata)
    actual = score_batch(export.to_csv(index=False).encode(), model, .2, summary)
    assert actual.observation.tolist() == [1]
    assert actual.score_classe_1.iloc[0] == pytest.approx(model.predict_proba(row)[0, 1])
    assert actual.classe.iloc[0] == (actual.score_classe_1.iloc[0] >= .2)
    assert not {'score', 'prediction', 'alerte', 'modele', 'seuil'} & set(actual.columns)


def test_visual_band_and_binary_decision_use_separate_thresholds(summary):
    class FixedScore:
        feature_names_in_ = summary.index
        classes_ = [1, 0]

        def predict_proba(self, frame):
            return np.array([[.35, .65]] * len(frame))

    payload = summary.initial.to_frame().T.to_csv(index=False).encode()
    frozen = score_batch(payload, FixedScore(), .2, summary)
    other = score_batch(payload, FixedScore(), .5, summary)
    assert (frozen.classe.iloc[0], other.classe.iloc[0]) == (1, 0)
    assert frozen.tranche_score.iloc[0] == other.tranche_score.iloc[0] == '[0.35, 0.50['
