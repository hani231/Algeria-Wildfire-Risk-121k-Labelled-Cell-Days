from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.eda_view import filter_training

ROOT = Path(__file__).resolve().parents[1]


def test_filters_never_include_future(small_data):
    filtered = filter_training(small_data, (2012, 2025), [1], months=[6], cells=['a'])
    assert len(filtered) == 2
    assert set(filtered.year) == {2012, 2013}
    assert set(filtered.label) == {1}
    assert set(filtered.cell_id) == {'a'}
    assert filter_training(small_data, (2012, 2023), []).empty
    assert filter_training(small_data, (2012, 2023), [0, 1], months=[]).empty


def test_real_dashboard_filters_and_empty_result():
    app = AppTest.from_file(str(ROOT / 'src/run_eda_demo.py'), default_timeout=60).run()
    assert len(app.exception) == 0
    assert app.metric[0].value == '104,979'
    assert len(app.dataframe) == 2
    app.slider(key='eda_years').set_range(2020, 2023).run()
    assert len(app.exception) == 0
    assert int(app.metric[0].value.replace(',', '')) < 104979
    app.multiselect(key='eda_labels').set_value([]).run()
    assert len(app.exception) == 0
    assert any('Aucune observation' in x.value for x in app.info)


def test_constant_and_missing_variable_dashboard():
    code = '''
import pandas as pd
from src.eda_view import render_eda
df = pd.DataFrame(dict(split=['train']*3, year=[2012]*3,
date=['2012-06-01','2012-06-02','2012-06-03'], label=[0,0,0],
cell_id=['a']*3, temp_max=[30.,30.,30.], ndvi=[float('nan')]*3))
render_eda(df)
'''
    app = AppTest.from_string(code, default_timeout=30).run()
    assert not app.exception
    app.selectbox(key='eda_variable').set_value('ndvi').run()
    assert not app.exception
    assert any('entièrement manquante' in x.value for x in app.info)
    app.multiselect(key='eda_months').set_value([]).run()
    assert not app.exception
    assert any('Aucune observation' in x.value for x in app.info)
