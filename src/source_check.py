"""Comparer le CSV du projet avec l'échantillon du producteur et l'historique visible."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.models import digest
from src.siad03_extensions.data import ROOT

KEY = ['cell_id', 'date']
FIELDS = ['days_since_last_fire', 'ndvi', 'ndvi_normal', 'ndvi_anomaly', 'ndvi_change_32d', 'ndvi_stale_days']


def verify(raw_path, sample_path):
    raw = pd.read_csv(raw_path, parse_dates=['date'])
    sample = pd.read_csv(sample_path, parse_dates=['date'])
    dev = raw[raw.year <= 2024]
    public = sample[sample.year <= 2024]
    matches = dev.merge(public, on=KEY, validate='one_to_one', suffixes=('', '_sample'))
    differences = {key: int((~np.isclose(matches[key], matches[key+'_sample'], equal_nan=True)).sum())
                   for key in FIELDS}
    train = dev[dev.year <= 2023]
    visible = divergent = 0
    for _, group in train.groupby('cell_id'):
        days = group.date.to_numpy(dtype='datetime64[D]')
        positives = np.sort(days[group.label.eq(1)])
        indices = np.searchsorted(positives, days - np.timedelta64(4, 'D'), side='left') - 1
        valid = indices >= 0
        age = (days[valid] - positives[indices[valid]]).astype(int)
        visible += int(valid.sum())
        divergent += int((age != group.days_since_last_fire.to_numpy()[valid]).sum())
    return dict(raw_sha256=digest(raw_path), sample_sha256=digest(sample_path),
                public_development=len(public), matched=len(matches), differences=differences,
                visible_history=visible, different_history=divergent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sample', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(ROOT/'Dataset/dataset.csv', args.sample), indent=2))
