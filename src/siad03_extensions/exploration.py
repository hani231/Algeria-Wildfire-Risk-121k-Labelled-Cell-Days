"""Dénominateurs spatio-temporels et dérive descriptive, sans inférence par ligne."""
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.statistical_analysis import analyse_training
from src.siad03_extensions.data import load_development, new_output, write_json


def summarize(df, by):
    out = df.groupby(by, observed=True).agg(n=('label', 'size'), detections=('label', 'sum'),
        cells=('cell_id', 'nunique')).reset_index()
    out['sample_fraction'] = out.detections / out.n
    return out


def drift(train, val, features):
    rows = []
    for col in features:
        a, b = train[col].dropna(), val[col].dropna()
        scale = a.std(ddof=1)
        rows.append(dict(variable=col, train_mean=a.mean(), val_mean=b.mean(),
            standardized_shift=(b.mean()-a.mean())/scale if scale > 0 else np.nan,
            train_missing=train[col].isna().mean(), val_missing=val[col].isna().mean(),
            val_outside_train_range=((b < a.min()) | (b > a.max())).mean()))
    return pd.DataFrame(rows)


def run(output):
    out = new_output(output)
    train, val, features, provenance = load_development()
    train['month'] = train.date.dt.month
    annual, monthly = summarize(train, ['year']), summarize(train, ['year', 'month'])
    cells = summarize(train, ['cell_id']).merge(train.groupby('cell_id')[['lat', 'lon']].first(), on='cell_id')
    if train.groupby('cell_id')[['lat', 'lon']].nunique().gt(1).any().any():
        raise ValueError('Coordonnées non constantes dans une cellule.')
    annual.to_csv(out/'annual.csv', index=False); monthly.to_csv(out/'monthly.csv', index=False)
    cells.to_csv(out/'cells.csv', index=False)
    summarize(train, ['cell_id', 'month']).to_csv(out/'cell_month.csv', index=False)
    shifts = drift(train, val, features); shifts.to_csv(out/'drift_2024.csv', index=False)
    for monthly_match, suffix in [(False, 'annual'), (True, 'matched_month')]:
        stats, gaps, counts = analyse_training(train, match_month=monthly_match)
        stats.to_csv(out/f'statistics_{suffix}.csv', index=False)
        gaps.to_csv(out/f'gaps_{suffix}.csv'); counts.to_csv(out/f'paired_cells_{suffix}.csv')
    write_json(out/'provenance.json', {**provenance,
        'train_prevalence': float(train.label.mean()), 'val_prevalence': float(val.label.mean()),
        'val_unseen_cell_rows': int((~val.cell_id.isin(train.cell_id)).sum()),
        'val_unseen_cells': int(val.loc[~val.cell_id.isin(train.cell_id), 'cell_id'].nunique()),
        'train_months': sorted(train.month.unique().tolist()),
        'interpretation': 'Proportions de détection dans un échantillon sélectionné ; pas de risque territorial.'})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].bar(annual.year, annual.n, color='#355c7d'); axes[0].set(title='Combien de cellules-jours sont échantillonnées ?', ylabel='Observations train', xlabel='Année')
    axes[1].plot(annual.year, annual.sample_fraction, marker='o', color='#bc5038'); axes[1].set(title='Quelle proportion porte une détection ?', ylabel='Proportion dans l’échantillon', xlabel='Année', ylim=(0,1))
    fig.tight_layout(); fig.savefig(out/'annual.png', dpi=150); plt.close(fig)
    matrix = monthly.pivot(index='year', columns='month', values='sample_fraction').reindex(columns=range(1,13))
    fig, ax = plt.subplots(figsize=(9, 5)); im = ax.imshow(matrix, aspect='auto', vmin=0, vmax=1, cmap='YlOrRd')
    ax.set(xticks=range(12), xticklabels=range(1,13), yticks=range(len(matrix)), yticklabels=matrix.index,
        xlabel='Mois (blanc = absence de données)', ylabel='Année', title='Saisonnalité observée — proportion échantillonnée')
    fig.colorbar(im, ax=ax, label='Détections / observations'); fig.tight_layout(); fig.savefig(out/'seasonality.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9,6)); sc = ax.scatter(cells.lon, cells.lat, c=cells.sample_fraction,
        s=8 + 3*np.sqrt(cells.n), cmap='YlOrRd', vmin=0, vmax=1, alpha=.7)
    ax.set(xlabel='Longitude (°)', ylabel='Latitude (°)', title='Cellules observées : couleur = proportion, taille = effectif')
    ax.set_aspect(1/np.cos(np.deg2rad(cells.lat.mean())))
    fig.colorbar(sc, ax=ax, label='Détections / observations (train)')
    fig.tight_layout(); fig.savefig(out/'cells.png', dpi=150); plt.close(fig)
    shifts = shifts.sort_values('standardized_shift')
    fig, ax = plt.subplots(figsize=(9,7)); ax.barh(shifts.variable, shifts.standardized_shift, color='#355c7d')
    ax.axvline(0, color='black', lw=.8); ax.set(title='Décalage 2024 par rapport au train', xlabel='(Moyenne 2024 − moyenne train) / écart-type train')
    fig.tight_layout(); fig.savefig(out/'drift.png', dpi=150); plt.close(fig)
    print(annual.to_string(index=False)); print('Coverage:', (out/'provenance.json').read_text())


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', default='results/siad03_extensions/exploration')
    run(p.parse_args().output)
