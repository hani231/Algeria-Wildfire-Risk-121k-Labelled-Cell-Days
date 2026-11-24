import json

import pandas as pd
import pytest

from src.models import CONFIG, LOT
from src.validation_alerts import published_alerts, summarize_alerts


def test_published_thresholds_counts_and_reliability():
    tables = published_alerts()
    thresholds = tables['thresholds'].set_index('threshold')
    frozen = json.loads((LOT / 'decision.json').read_text())
    published = pd.read_csv(LOT / 'thresholds_2024.csv')
    for row in published[published.model.eq(frozen['model'])].itertuples():
        assert thresholds.loc[row.threshold, 'f1'] == pytest.approx(row.f1)
    assert thresholds.index.tolist() == json.loads(CONFIG.read_text())['thresholds']
    assert thresholds.fp.is_monotonic_decreasing and thresholds.fn.is_monotonic_increasing
    counts = ['tp', 'fn', 'fp', 'tn']
    expected = thresholds.loc[frozen['threshold']]
    assert expected[counts].sum() == expected.n == 8423
    assert tables['months'][counts].sum().tolist() == expected[counts].tolist()
    bins = tables['reliability']
    assert bins.n.sum() == expected.n
    assert (bins.n * bins.observed).sum() == pytest.approx(expected.positives)


@pytest.mark.parametrize('column', ['year', 'date'])
def test_rejects_mixed_cohort(column):
    scores = pd.read_csv(LOT / 'predictions_validation.csv', nrows=2)
    scores.loc[0, column] = 2025 if column == 'year' else '2025-06-01'
    with pytest.raises(ValueError, match='2024'):
        summarize_alerts(scores, 'SVM', .2, [.2])
