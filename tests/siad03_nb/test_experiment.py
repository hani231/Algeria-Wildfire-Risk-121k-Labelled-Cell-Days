import numpy as np
import pandas as pd
from src.siad03_nb.experiment import nb_pipeline, fit_models, SMOOTHING


def test_imputer_is_fitted_on_training_only():
    train = pd.DataFrame({'x': [1., 3., np.nan, 5.], 'empty': [np.nan]*4})
    model = nb_pipeline().fit(train, [0, 0, 1, 1])
    before = model.named_steps['imputer'].statistics_.copy()
    prediction = model.predict_proba(pd.DataFrame({'x': [100000., np.nan], 'empty': [7., np.nan]}))
    np.testing.assert_array_equal(before, [3., 0.])
    np.testing.assert_array_equal(model.named_steps['imputer'].statistics_, before)
    assert np.isfinite(prediction).all()


def test_selection_and_majority_baseline(small_data):
    train = small_data.loc[small_data.split.eq('train')].reset_index(drop=True)
    folds = [(np.flatnonzero(train.year.eq(2012)), np.flatnonzero(train.year.eq(2013)))]
    models, search, baseline = fit_models(train, ['temp_max', 'rh_mean'], folds, [1e-9, 1.])
    assert search.best_score_ == max(search.cv_results_['mean_test_f1'])
    assert search.n_splits_ == 1  # Small synthetic unit fixture; production contract requires five.
    majority = train.label.value_counts().sort_index().idxmax()
    assert (models['Zero-R'].predict(train[['temp_max', 'rh_mean']]) == majority).all()
    assert len(baseline['test_f1']) == 1
    assert set([1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2]).issubset(SMOOTHING)
    assert max(SMOOTHING) > .01
