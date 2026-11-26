"""Validation du lot et distribution des scores du studio IASD17."""
import json

import streamlit as st

from src.explainability.alert_levels import alert_labels, load_thresholds
from src.ui.services import CONFIG, input_summary, score_measures, validate_measures


def protocol_features() -> list:
    return list(json.loads(CONFIG.read_text(encoding='utf-8'))['features'])


def validate_batch(frame, features, *, allow_missing=False):
    return validate_measures(frame, features, allow_missing=allow_missing)


def predict_batch(model, frame, threshold, *, summary=None, allow_missing=False):
    features = list(model.feature_names_in_)
    values = validate_batch(frame, features, allow_missing=allow_missing)
    if summary is not None:
        outside = values.lt(summary.minimum, axis='columns') | values.gt(summary.maximum, axis='columns')
        if outside.any().any():
            rows, columns = outside.to_numpy().nonzero()
            raise ValueError(f'Observation {rows[0] + 1} : {features[columns[0]]} sort de la plage du formulaire.')
    labels, scores = score_measures(model, values, threshold)
    result = values.assign(classe=labels)
    if scores is not None:
        result['score_classe_1'] = scores
        result['tranche_score'] = alert_labels(scores)
    result.insert(0, 'observation', range(1, len(result) + 1))
    return result


def example_csv(features) -> bytes:
    sample = input_summary(tuple(features)).initial.to_frame().T
    return sample.to_csv(index=False).encode('utf-8')


def score_distribution(result):
    """Montrer chaque tranche, y compris celles sans observation."""
    cuts = load_thresholds()
    counts = result['tranche_score'].value_counts().reindex(alert_labels([0., *cuts], cuts), fill_value=0)
    st.dataframe(counts.rename('Observations').rename_axis('Tranche du score').reset_index(),
                 hide_index=True, width='stretch')
