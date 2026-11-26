"""Vérifier l'alignement et les dénominateurs des diagnostics 2024."""
import pandas as pd
import pytest

from src.development_profiles import align_scores, MEASURES
from src.models import LOT


@pytest.fixture
def frames():
    val = pd.DataFrame({'cell_id': ['A', 'B'], 'date': pd.to_datetime(['2024-06-01'] * 2),
                        'year': 2024, 'label': [0, 1]})
    return val, val.iloc[::-1].assign(SVM=[.7, .1]).copy()


def test_match_uses_cell_and_date_not_order(frames):
    val, scores = frames
    assert align_scores(val, scores, 'SVM').set_index('cell_id').SVM.to_dict() == {'A': .1, 'B': .7}


@pytest.mark.parametrize('column,value', [('year', 2025), ('date', pd.Timestamp('2025-06-01')),
                                         ('label', 0), ('cell_id', 'A'), ('SVM', float('inf'))])
def test_rejects_foreign_scores_and_invalid_keys(frames, column, value):
    val, scores = frames
    scores.iloc[0, scores.columns.get_loc(column)] = value
    with pytest.raises(ValueError):
        align_scores(val, scores, 'SVM')


def test_published_strata_partition_validation_and_report_missingness():
    folder = LOT.parent / 'post_freeze' / 'development_profiles'
    errors = pd.read_csv(folder / 'erreurs_2024.csv')
    decision = pd.read_json(LOT / 'decision.json', typ='series')
    scores = pd.read_csv(LOT / 'predictions_validation.csv')
    pred = scores[decision['model']].ge(decision['threshold'])
    pos = scores.label.eq(1)
    expected = [(pos & pred).sum(), (~pos & pred).sum(), (pos & ~pred).sum(), (~pos & ~pred).sum()]
    assert set(errors.dimension) == {'bloc_1_degre', *MEASURES}
    for _, rows in errors.groupby('dimension'):
        assert rows[['tp', 'fp', 'fn', 'tn']].sum().tolist() == expected
    months = pd.read_csv(folder / 'distributions_mensuelles.csv')
    assert set(months.month) == {6, 7, 8, 9, 10}
    assert months.measured.le(months.n).all()
    assert set(months[months.cohort.eq('Validation')].groupby('variable').n.sum()) == {len(scores)}
    geography = pd.read_csv(folder / 'geographie.csv')
    assert geography.groupby('cohort').n.sum().to_dict() == {'Train': 104979, 'Validation': len(scores)}
