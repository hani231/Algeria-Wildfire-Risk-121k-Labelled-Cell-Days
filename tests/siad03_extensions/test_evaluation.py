import numpy as np
import pytest
from src.siad03_extensions.evaluation import metrics, calibration, cluster_intervals


def test_confusion_and_calibration_edges():
    m = metrics([0, 0, 1, 1], [0, .7, .3, 1])
    assert [m[k] for k in ['tn', 'fp', 'fn', 'tp']] == [1, 1, 1, 1]
    assert m['f1'] == .5 and m['balanced_accuracy'] == .5
    c = calibration([0, 1], [0, 1]); assert c.n.sum() == 2
    assert np.isnan(metrics([0, 0], [.1, .2])['roc_auc'])


@pytest.mark.parametrize('score', [[np.nan, .2], [-.1, .5], [0, 2]])
def test_invalid_scores(score):
    with pytest.raises(ValueError): metrics([0, 1], score)


def test_block_bootstrap_deterministic():
    y = np.tile([0, 1], 5); p = np.tile([.1, .9], 5); g = np.repeat(np.arange(5), 2)
    a = cluster_intervals(y, p, g, repeats=20)
    assert a.equals(cluster_intervals(y, p, g, repeats=20))
    assert a.loc[a.metric.eq('f1'), 'low'].iloc[0] == 1
    with pytest.raises(ValueError): cluster_intervals(y, p, np.zeros(10))
