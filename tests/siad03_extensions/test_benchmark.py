import numpy as np
import pandas as pd
from sklearn.base import clone
from src.siad03_extensions.benchmark import candidates
from src.train_decision_tree import build_temporal_splits


def test_candidates_handle_missing_and_produce_probabilities():
    rng = np.random.default_rng(42)
    x = pd.DataFrame(rng.normal(size=(200, 4))); x.iloc[0, 0] = np.nan
    y = np.tile([0, 1], 100)
    for estimator, grid in candidates().values():
        model = clone(estimator).fit(x, y)
        p = model.predict_proba(x)
        assert p.shape == (200, 2) and np.isfinite(p).all()
        assert len(grid) >= 2


def test_five_folds_preserve_chronology():
    frame = pd.DataFrame([(pd.Timestamp(y, 6, d), y, d % 2) for y in range(2012, 2024)
        for d in range(1, 5)], columns=['date', 'year', 'label'])
    folds = build_temporal_splits(frame, [2019, 2020, 2021, 2022, 2023])
    assert len(folds) == 5
    for tr, va in folds:
        assert frame.iloc[tr].date.max() < frame.iloc[va].date.min()
        assert not set(tr).intersection(va)
