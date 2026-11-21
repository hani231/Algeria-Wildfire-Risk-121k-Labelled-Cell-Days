"""Unités établies dans docs/dictionnaire_colonnes.md."""
UNITS = {
    **dict.fromkeys(('temp_min', 'temp_max', 'temp_mean', 'temp_max_7d_mean'), '°C'),
    **dict.fromkeys(('wind_mean', 'wind_max'), 'km/h'),
    **dict.fromkeys(('precip_sum', 'precip_7d', 'precip_30d'), 'mm'),
    'vpd_max': 'kPa',
    'rh_min': '%', 'rh_mean': '%', 'rh_min_7d_mean': '%',
    'days_since_rain_1mm': 'jours', 'ndvi_stale_days': 'jours',
    'doy': 'jour de l’année', 'ndvi': 'sans unité', 'ndvi_change_32d': 'sans unité',
    **dict.fromkeys(('ffmc', 'dmc', 'dc', 'isi', 'bui', 'fwi'), 'indice'),
}


def measure_label(name):
    return f"{name} ({UNITS.get(name, 'unité source à confirmer')})"
