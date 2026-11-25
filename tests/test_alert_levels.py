import json
import pytest
from src.explainability.alert_levels import (alert_badge, alert_labels,
                                             alert_level, load_thresholds)
from src.ui.services import CONFIG


def test_thresholds_match_protocol():
    thresholds = load_thresholds()
    assert thresholds == (0.2, 0.35, 0.5)
    assert list(thresholds) == json.loads(CONFIG.read_text(encoding='utf-8'))['thresholds']


@pytest.mark.parametrize('score,expected', [
    (0.0, 'Faible'), (0.199, 'Faible'), (0.2, 'Modéré'), (0.349, 'Modéré'),
    (0.35, 'Élevé'), (0.499, 'Élevé'), (0.5, 'Critique'), (1.0, 'Critique')])
def test_alert_boundaries(score, expected):
    assert alert_level(score).label == expected


def test_level_keys_colors_and_description():
    level = alert_level(0.6)
    assert level.key == 'critique'
    assert level.color == '#c92a2a'
    assert '0.50' in level.description


def test_badge_contains_label_and_color():
    badge = alert_badge(0.6)
    assert 'Critique' in badge and '#c92a2a' in badge
    assert alert_badge(0.1).count('#2b8a3e') == 1


def test_alert_labels_series():
    assert alert_labels([0.1, 0.3, 0.4, 0.9]) == ['Faible', 'Modéré', 'Élevé', 'Critique']


def test_custom_thresholds_respected():
    assert alert_level(0.3, thresholds=(0.1, 0.2, 0.9)).label == 'Élevé'


@pytest.mark.parametrize('score', [-0.1, 1.1, float('nan'), float('inf'), 'x', None])
def test_invalid_scores_rejected(score):
    with pytest.raises(ValueError):
        alert_level(score)


def test_bad_thresholds_rejected(tmp_path):
    path = tmp_path/'protocole.json'
    path.write_text(json.dumps({'thresholds': [0.5, 0.3, 0.2]}), encoding='utf-8')
    with pytest.raises(ValueError, match='trois seuils'):
        load_thresholds(path)
