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
    (0.0, '[0.00, 0.20['), (0.199, '[0.00, 0.20['), (0.2, '[0.20, 0.35['), (0.349, '[0.20, 0.35['),
    (0.35, '[0.35, 0.50['), (0.499, '[0.35, 0.50['), (0.5, '[0.50, 1.00]'), (1.0, '[0.50, 1.00]')])
def test_alert_boundaries(score, expected):
    assert alert_level(score).label == expected


def test_level_keys_colors_and_description():
    level = alert_level(0.6)
    assert level.key == 'tranche_4'
    assert level.color == '#354969'
    assert '0.50' in level.description


def test_badge_contains_label_and_color():
    badge = alert_badge(0.6)
    assert '[0.50, 1.00]' in badge and '#354969' in badge
    assert alert_badge(0.1).count('#354969') == 1


def test_alert_labels_series():
    assert alert_labels([0.1, 0.3, 0.4, 0.9]) == ['[0.00, 0.20[', '[0.20, 0.35[', '[0.35, 0.50[', '[0.50, 1.00]']


def test_custom_thresholds_respected():
    assert alert_level(0.3, thresholds=(0.1, 0.2, 0.9)).label == '[0.20, 0.90['


@pytest.mark.parametrize('score', [-0.1, 1.1, float('nan'), float('inf'), 'x', None])
def test_invalid_scores_rejected(score):
    with pytest.raises(ValueError):
        alert_level(score)


def test_bad_thresholds_rejected(tmp_path):
    path = tmp_path/'protocole.json'
    path.write_text(json.dumps({'thresholds': [0.5, 0.3, 0.2]}), encoding='utf-8')
    with pytest.raises(ValueError, match='trois seuils'):
        load_thresholds(path)
