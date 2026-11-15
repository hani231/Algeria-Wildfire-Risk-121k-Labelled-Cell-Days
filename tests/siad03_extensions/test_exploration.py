import pandas as pd
from src.siad03_extensions.exploration import summarize, drift


def test_denominators_and_missing_groups():
    df = pd.DataFrame({'cell_id':['a','a','b'], 'label':[1,0,1], 'year':[2020,2020,2021]})
    a = summarize(df, ['year'])
    assert a.n.sum() == 3 and a.detections.sum() == 2
    assert a.sample_fraction.tolist() == [.5, 1]
    assert summarize(df.iloc[:0], ['year']).empty


def test_drift_uses_training_scale():
    a = pd.DataFrame({'x':[0.,2.]}); b = pd.DataFrame({'x':[4.,6.]})
    d = drift(a,b,['x']).iloc[0]
    assert d.val_outside_train_range == 1
    assert d.standardized_shift == 4/a.x.std()
