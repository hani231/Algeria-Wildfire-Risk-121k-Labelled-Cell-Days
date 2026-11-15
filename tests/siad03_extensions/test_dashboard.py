from streamlit.testing.v1 import AppTest
from src.siad03_extensions.data import ROOT


def test_scientific_dashboard_empty_filter_and_metrics():
    app = AppTest.from_file(str(ROOT/'src/siad03_extensions/dashboard.py'), default_timeout=60).run()
    assert not app.exception
    assert app.metric[0].value == '104,979'
    app.multiselect(key='science_months').set_value([]).run()
    assert not app.exception
    assert any('Aucune observation pour cette sélection' in item.value for item in app.info)
