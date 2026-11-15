"""Audit reproductible du CSV brut ; ne modifie jamais la source."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from src.cleaning_guide import clean_data


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('Dataset/dataset.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/audit_siad03'))
    args = parser.parse_args()
    raw = pd.read_csv(args.data)
    clean, report = clean_data(raw)
    args.output.mkdir(parents=True, exist_ok=True)
    report.update(source=args.data.as_posix(), sha256_brut=sha256_file(args.data),
                  zones=int(clean.cell_id.nunique()),
                  debut=str(clean.date.min().date()), fin=str(clean.date.max().date()),
                  lignes_par_partition={k: int(v) for k, v in clean.groupby('split').size().items()},
                  effectifs_train={str(k): int(v) for k, v in clean.loc[clean.split.eq('train'), 'label'].value_counts().items()},
                  controles_appris_sur_test=False)
    if 'days_since_last_fire' in raw:
        report['code_special_9999'] = int(raw.days_since_last_fire.eq(9999).sum())
    audit = pd.DataFrame({'type': raw.dtypes.astype(str), 'manquants': raw.isna().sum(),
                          'pourcentage_manquant': raw.isna().mean() * 100,
                          'valeurs_distinctes': raw.nunique()})
    audit.to_csv(args.output / 'colonnes.csv', index_label='colonne')
    for column in ['sample_kind', 'n_detections', 'max_frp']:
        if column not in raw:
            continue
        values = (raw[column].gt(0) if column == 'n_detections' else
                  raw[column].notna() if column == 'max_frp' else raw[column])
        pd.crosstab(raw.label, values).to_csv(args.output / f'fuite_{column}.csv')
    (args.output / 'qualite.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
