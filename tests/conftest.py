import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def small_data():
    rows = []
    for year in [2012, 2013, 2024, 2025]:
        for month in [6, 7]:
            for cell in ['a', 'b']:
                for label in [0, 1]:
                    date = pd.Timestamp(year=year, month=month, day=label + 1)
                    rows.append(dict(cell_id=cell, date=str(date.date()), year=year,
                                     doy=date.dayofyear, label=label,
                                     split='train' if year < 2024 else 'val' if year == 2024 else 'test',
                                     temp_min=10., temp_mean=20., temp_max=30. + label,
                                     rh_min=20., rh_mean=50. - label,
                                     wind_mean=1., wind_max=2., precip_sum=0., ndvi=np.nan,
                                     days_since_last_fire=9999, sample_kind='positive' if label else 'matched_negative',
                                     n_detections=label, max_frp=5. if label else np.nan))
    return pd.DataFrame(rows)
