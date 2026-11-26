"""Maintenir la population et l'explication choisies au retour d'une autre page."""
from streamlit.testing.v1 import AppTest

from src.ui.services import ROOT


def test_return_preserves_arena_cohort_and_shap_sample():
    app = AppTest.from_file(str(ROOT / 'src/app.py'), default_timeout=180).run()
    app.radio(key='page').set_value('Modèles').run()
    app.radio(key='arena_cohort').set_value('Test final 2025').run()
    app.radio(key='page').set_value('Explicabilité').run()
    app.selectbox(key='shap_model').set_value('Random Forest').run()
    app.selectbox(key='shap_rows').set_value(50).run()
    app.radio(key='page').set_value('Modèles').run()
    assert app.radio(key='arena_cohort').value == 'Test final 2025'
    app.radio(key='page').set_value('Explicabilité').run()
    assert app.selectbox(key='shap_model').value == 'Random Forest'
    assert app.selectbox(key='shap_rows').value == 50
    assert not app.error and not app.exception
