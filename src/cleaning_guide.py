"""Nettoyage déterministe, sans moyenne ni médiane apprise sur les données."""
import numpy as np
import pandas as pd
from src.data_quality import METADATA, NUMERIC_COLUMNS, coherence_counts

LEAKAGE_COLUMNS = ['sample_kind', 'n_detections', 'max_frp']

def clean_data(raw):
    if not isinstance(raw, pd.DataFrame):
        raise ValueError('Les données doivent être un tableau pandas.')
    df = raw.copy(deep=True)
    report = {'lignes_avant': len(df), 'colonnes_avant': len(df.columns)}
    if not all(isinstance(c, str) for c in df.columns):
        raise ValueError('Les noms de colonnes doivent être du texte.')
    df.columns = df.columns.str.strip()
    if df.columns.duplicated().any():
        raise ValueError('Noms de colonnes répétés après suppression des espaces.')
    missing = METADATA.difference(df.columns)
    if missing:
        raise ValueError(f'Colonnes obligatoires absentes : {sorted(missing)}')
    if df.empty:
        raise ValueError('Le fichier ne contient aucune observation.')
    for col in sorted(NUMERIC_COLUMNS.intersection(df.columns)):
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except (ValueError, TypeError) as exc:
            raise ValueError(f'La colonne {col} doit contenir des nombres ou des valeurs manquantes.') from exc
    # On supprime uniquement un ancien index d'export dont on a vérifié le contenu.
    if 'Unnamed: 0' in df.columns:
        if not np.array_equal(df['Unnamed: 0'].to_numpy(), np.arange(len(df))):
            raise ValueError('Unnamed: 0 ne ressemble pas à un simple index. Examiner cette colonne.')
        df = df.drop(columns='Unnamed: 0')
    try:
        df['date'] = pd.to_datetime(df['date'], errors='raise', format='ISO8601')
    except (ValueError, TypeError) as exc:
        raise ValueError('La colonne date contient une date invalide.') from exc
    if df['date'].isna().any() or df['cell_id'].isna().any():
        raise ValueError('Une observation ne possède pas de date ou de zone.')
    if df['cell_id'].astype(str).str.strip().eq('').any():
        raise ValueError('Une observation possède une zone vide.')
    if df['date'].dt.tz is not None or not df['date'].eq(df['date'].dt.normalize()).all():
        raise ValueError('date doit représenter un jour sans heure ni fuseau horaire.')
    if not df['label'].isin([0, 1]).all():
        raise ValueError('La cible doit être 0 ou 1, sans valeur manquante.')
    if not df['split'].isin(['train', 'val', 'test']).all():
        raise ValueError('Partition inconnue.')
    report['doublons_exacts_supprimes'] = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    if df.duplicated(['cell_id', 'date']).any():
        raise ValueError('Plusieurs lignes différentes ont la même clé (cell_id, date). Examiner le conflit.')
    if not (df['year'].eq(df['date'].dt.year) & df['doy'].eq(df['date'].dt.dayofyear)).all():
        raise ValueError('Incohérence entre date, year et doy.')
    expected = np.where(df['year'] <= 2023, 'train', np.where(df['year'] == 2024, 'val', 'test'))
    if not (df['year'].between(2012, 2025).all() and np.array_equal(expected, df['split'])):
        raise ValueError('Le découpage temporel diffère de la version étudiée.')
    report['controles_coherence'] = coherence_counts(df)
    anomalies = {key: value for key, value in report['controles_coherence'].items() if value}
    if anomalies:
        raise ValueError(f'Incohérences à examiner avant nettoyage : {anomalies}')
    report['colonnes_fuite_exclues'] = [c for c in LEAKAGE_COLUMNS if c in df.columns]
    df = df.drop(columns=LEAKAGE_COLUMNS, errors='ignore')
    # Les NaN restent présents. L'imputation sera apprise dans le pipeline.
    # 9999 reste documenté comme valeur spéciale, sans inventer une durée réelle.
    report.update(lignes_apres=len(df), colonnes_apres=len(df.columns))
    return df, report
