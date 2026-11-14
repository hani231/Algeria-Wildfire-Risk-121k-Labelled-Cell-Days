import numpy as np
import pytest
from pandas.testing import assert_frame_equal

from src.statistical_analysis import analyse_training, holm_adjust


def test_holm_known_example_and_missing():
    np.testing.assert_allclose(holm_adjust([.03, .01, .04]), [.06, .03, .06])
    np.testing.assert_allclose(holm_adjust([.01, np.nan]), [.02, np.nan], equal_nan=True)
    assert len(holm_adjust([])) == 0


@pytest.mark.parametrize('values', [[-1], [1.2], [np.inf]])
def test_holm_invalid(values):
    with pytest.raises(ValueError):
        holm_adjust(values)


def test_known_effects_and_future_ignored(small_data):
    summary, gaps, counts = analyse_training(small_data)
    assert summary.ecart_annuel_moyen.tolist() == [1., -1.]
    assert summary.annees_non_nulles.tolist() == [2, 2]
    assert summary.annees_ecart_positif.tolist() == [2, 0]
    assert (counts == 2).all().all()
    changed = small_data.copy()
    changed.loc[changed.split.ne('train'), ['temp_max', 'rh_mean']] = 999
    for before, after in zip((summary, gaps, counts), analyse_training(changed)):
        assert_frame_equal(before, after)


def test_missing_class_and_zero_effects_are_not_significant(small_data):
    no_positive = small_data.loc[small_data.label.eq(0)]
    results, _, _ = analyse_training(no_positive)
    assert results.annees_non_nulles.eq(0).all()
    assert results.p_holm.isna().all()
    constant = small_data.assign(temp_max=30., rh_mean=50.)
    results, _, _ = analyse_training(constant)
    assert results.annees_ecart_nul.eq(2).all()
    assert results.p_holm.isna().all()


def test_monthly_matching_controls_simple_season_confounding(small_data):
    train = small_data.loc[small_data.split.eq('train')].copy()
    # In each month the classes have the same values, but the mix of months differs.
    train['temp_max'] = np.where(train.date.str[5:7].eq('07'), 40., 20.)
    train = train.loc[~(train.date.str[5:7].eq('06') & train.label.eq(1))]
    principal, _, _ = analyse_training(train)
    monthly, _, _ = analyse_training(train, match_month=True)
    assert principal.iloc[0].ecart_annuel_moyen == 10
    assert monthly.iloc[0].ecart_annuel_moyen == 0


def test_illegal_train_year_rejected(small_data):
    with pytest.raises(ValueError, match='2012-2023'):
        analyse_training(small_data.assign(split='train'))
