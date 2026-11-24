import json

import numpy as np
import pandas as pd
import pytest

from src.kfold_diagnostic import diagnostic_folds
from src.models import CONFIG, LOT, MANDATORY
from src.siad03_extensions.data import ROOT


def test_kfold_holds_out_each_row_once_and_rejects_future():
    train = pd.DataFrame({'year': np.tile([2019, 2020], 50),
                          'split': 'train', 'label': np.tile([0, 1], 50)})
    folds = diagnostic_folds(train, 25, 42)
    np.testing.assert_array_equal(np.sort(np.concatenate([check for _, check in folds])), np.arange(100))
    for fit, check in folds:
        assert len(fit) == 25 and not np.intersect1d(fit, check).size
    for year, split in [(2024, 'val'), (2025, 'test'), (2025, 'train')]:
        with pytest.raises(ValueError, match='exclusivement'):
            diagnostic_folds(train.assign(year=year, split=split), None, 42)


def test_complementary_grid_records_frozen_configuration():
    from ast import literal_eval
    root = ROOT/'results/post_freeze/kfold_train'
    summary = pd.read_csv(root/'folds.csv')
    manifest = json.loads((LOT/'manifest.json').read_text())['models']
    caps = json.loads(CONFIG.read_text())['train_caps']
    assert set(summary.model) == set(MANDATORY)
    for name, rows in summary.groupby('model'):
        assert list(rows.fold) == [1,2,3,4,5]
        assert rows.n_check.sum() == 104979
        if name in caps:
            assert rows.n_fit.eq(caps[name]).all()
        assert rows.first_check_year.eq(2012).all() and rows.last_fit_year.eq(2023).all()
        grid = pd.read_csv(root/f'{name}.csv')
        frozen = grid[grid.params.map(literal_eval).map(lambda params: params == manifest[name]['params'])].iloc[0]
        for i, row in enumerate(rows.itertuples()):
            assert row.f1_check == pytest.approx(frozen[f'split{i}_test_score'])
            assert row.f1_fit == pytest.approx(frozen[f'split{i}_train_score'])
