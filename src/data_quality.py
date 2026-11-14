"""Contrôles déterministes : aucune statistique apprise sur train/val/test."""
from __future__ import annotations

import numpy as np
import pandas as pd

METADATA = {"cell_id", "date", "year", "doy", "label", "split"}
NUMERIC_COLUMNS = {
    "lat", "lon", "year", "doy", "label", "n_detections", "max_frp",
    "temp_max", "temp_min", "temp_mean", "rh_min", "rh_mean", "wind_max",
    "wind_mean", "precip_sum", "vpd_max", "precip_7d", "precip_30d",
    "days_since_rain_1mm", "temp_max_7d_mean", "rh_min_7d_mean", "ffmc",
    "dmc", "dc", "isi", "bui", "fwi", "days_since_last_fire", "ndvi",
    "ndvi_normal", "ndvi_anomaly", "ndvi_change_32d", "ndvi_stale_days",
}


def coherence_counts(df: pd.DataFrame) -> dict[str, int]:
    """Compter les impossibilités connues, sans assimiler extrême et erreur.

    Les NaN des prédicteurs restent autorisés pour l'imputation dans les plis.
    Les unités du vent, de VPD et des indices FWI ne sont pas supposées connues.
    """
    checks = {"valeurs_infinies": int(np.isinf(
        df.select_dtypes("number").to_numpy(dtype=float, na_value=np.nan)
    ).sum())}
    bounds = {"rh_min": (0, 100), "rh_mean": (0, 100),
              "rh_min_7d_mean": (0, 100), "ndvi": (-1, 1),
              "ndvi_normal": (-1, 1), "lat": (-90, 90), "lon": (-180, 180)}
    for name, (low, high) in bounds.items():
        if name in df:
            checks[name + "_hors_limites"] = int(
                (df[name].notna() & ~df[name].between(low, high)).sum())
    for name in ["wind_max", "wind_mean", "precip_sum", "precip_7d",
                 "precip_30d", "days_since_rain_1mm", "days_since_last_fire",
                 "ndvi_stale_days"]:
        if name in df:
            checks[name + "_negatif"] = int(df[name].lt(0).sum())
    for lower, upper in [("temp_min", "temp_mean"), ("temp_mean", "temp_max"),
                         ("temp_min", "temp_max"), ("rh_min", "rh_mean"),
                         ("wind_mean", "wind_max")]:
        if {lower, upper}.issubset(df.columns):
            checks[lower + "_superieur_" + upper] = int(df[lower].gt(df[upper]).sum())
    return checks
