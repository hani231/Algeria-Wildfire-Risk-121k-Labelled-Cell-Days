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
