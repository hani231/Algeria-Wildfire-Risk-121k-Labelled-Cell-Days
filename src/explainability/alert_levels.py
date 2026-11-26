"""Tranches descriptives du score de classe, aux trois coupures du protocole."""
from bisect import bisect_right
from dataclasses import dataclass
from html import escape
import json
import math
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / 'config/protocole.json'


@dataclass(frozen=True)
class AlertLevel:
    key: str
    label: str
    color: str
    description: str


def load_thresholds(path=CONFIG) -> tuple:
    """Lit les trois bornes croissantes utilisées par le benchmark."""
    try:
        thresholds = tuple(float(value) for value in
                           json.loads(Path(path).read_text(encoding='utf-8'))['thresholds'])
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ValueError('Seuils de score illisibles dans le protocole.') from error
    if len(thresholds) != 3 or not 0 < thresholds[0] < thresholds[1] < thresholds[2] < 1:
        raise ValueError('Le protocole doit fournir trois seuils croissants entre 0 et 1.')
    return thresholds


def alert_level(score, thresholds=None) -> AlertLevel:
    """Situe le score sur une échelle descriptive commune aux modèles."""
    try:
        score = float(score)
    except (TypeError, ValueError) as error:
        raise ValueError('Le score doit être numérique.') from error
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError('Le score doit être compris entre 0 et 1.')
    cuts = load_thresholds() if thresholds is None else thresholds
    index = bisect_right(cuts, score)
    bounds = (0., *cuts, 1.)
    closing = ']' if index == len(cuts) else '['
    interval = f'[{bounds[index]:.2f}, {bounds[index+1]:.2f}{closing}'
    return AlertLevel(f'tranche_{index+1}', interval, '#354969',
                      f'Score de classe 1 dans la tranche {interval}.')


def alert_badge(score, thresholds=None) -> str:
    level = alert_level(score, thresholds)
    return (f'<span style="background:{level.color};color:#fff;padding:2px 8px;'
            f'border-radius:4px;font-weight:600;">Tranche du score · {escape(level.label)}</span>')


def alert_labels(scores, thresholds=None) -> list:
    cuts = load_thresholds() if thresholds is None else thresholds
    return [alert_level(score, cuts).label for score in scores]
