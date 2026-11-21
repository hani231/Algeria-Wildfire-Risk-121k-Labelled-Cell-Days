import numpy as np
import pandas as pd
from src.models import LOT
from src.siad03_extensions.data import ROOT
from src.source_check import verify


def test_learning_curves_reproduce_reference_sample():
    sizes = pd.read_csv(ROOT/'results/post_freeze/size_2024/learning_curves.csv')
    assert set(sizes.year) == {2024} and set(sizes.threshold) == {0.5}
    assert sizes.groupby(['model', 'n_fit']).seed.apply(set).map(lambda s: s == {42, 43, 44}).all()
    reference = pd.read_csv(LOT/'metrics.csv').set_index('model')
    for name, rows in sizes[sizes.seed == 42].groupby('model'):
        assert np.isclose(rows.loc[rows.n_fit.idxmax(), 'f1'], reference.loc[name, 'f1'])


def test_source_history_excludes_four_day_boundary(tmp_path):
    days = pd.date_range('2020-01-01', periods=6)
    frame = pd.DataFrame(dict(cell_id=1, date=days, year=2020, label=[1,0,0,0,0,0],
                              days_since_last_fire=[9999]*5+[5], ndvi=0.4, ndvi_normal=0.3,
                              ndvi_anomaly=0.1, ndvi_change_32d=0.1, ndvi_stale_days=1))
    path = tmp_path/'sample.csv'
    frame.to_csv(path, index=False)
    result = verify(path, path)
    assert result['matched'] == 6
    assert result['visible_history'] == 1 and result['different_history'] == 0
    assert not any(result['differences'].values())
