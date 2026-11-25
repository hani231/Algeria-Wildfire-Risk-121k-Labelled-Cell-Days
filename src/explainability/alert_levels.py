"""Niveaux d'alerte multi-seuils alignés sur config/protocole.json.

Le score du modèle n'est pas une probabilité d'incendie : il classe une
cellule-jour rétrospective. Les quatre niveaux traduisent la position du
score sur les seuils du protocole (0,20 / 0,35 / 0,50) pour la lecture.
"""
from dataclasses import dataclass
import json
import math
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / 'config/protocole.json'

COLORS = {'faible': '#2b8a3e', 'modere': '#f08c00',
          'eleve': '#e8590c', 'critique': '#c92a2a'}


@dataclass(frozen=True)
class AlertLevel:
    key: str
    label: str
    color: str
    description: str


def load_thresholds(path=CONFIG) -> tuple:
    """Lit les trois seuils croissants du protocole."""
    try:
        thresholds = tuple(float(value) for value in
                           json.loads(Path(path).read_text(encoding='utf-8'))['thresholds'])
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ValueError('Seuils d’alerte illisibles dans le protocole.') from error
    if len(thresholds) != 3 or not all(0 < a < b < 1 for a, b in zip(thresholds, thresholds[1:])):
        raise ValueError('Le protocole doit fournir trois seuils croissants entre 0 et 1.')
    return thresholds


def alert_level(score, thresholds=None) -> AlertLevel:
    """Mappe un score de classe sur le niveau d'alerte correspondant."""
    try:
        score = float(score)
    except (TypeError, ValueError) as error:
        raise ValueError('Le score doit être numérique.') from error
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError('Le score doit être compris entre 0 et 1.')
    low, mid, high = thresholds or load_thresholds()
    if score < low:
        key, description = 'faible', f'sous le seuil {low:.2f}'
    elif score < mid:
        key, description = 'modere', f'entre {low:.2f} et {mid:.2f}'
    elif score < high:
        key, description = 'eleve', f'entre {mid:.2f} et {high:.2f}'
    else:
        key, description = 'critique', f'à partir de {high:.2f}'
    labels = {'faible': 'Faible', 'modere': 'Modéré',
              'eleve': 'Élevé', 'critique': 'Critique'}
    return AlertLevel(key, labels[key], COLORS[key], description)


def alert_badge(score, thresholds=None) -> str:
    """Badge HTML coloré affiché sous la jauge du studio."""
    level = alert_level(score, thresholds)
    return (f'<span style="background:{level.color};color:#fff;padding:2px 8px;'
            f'border-radius:4px;font-weight:600;">Niveau d’alerte · {level.label}</span>')


def alert_labels(scores, thresholds=None) -> list:
    """Traduit une série de scores en libellés d'alerte."""
    return [alert_level(score, thresholds).label for score in scores]
