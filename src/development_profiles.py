"""Comparer les saisons de développement et décrire les erreurs du classifieur gelé."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models import LOT
from src.preprocessing import development_inputs
from src.siad03_extensions.data import new_output


MEASURES = {
    'temp_max': 'Température maximale (°C)', 'rh_mean': 'Humidité moyenne (%)',
    'precip_sum': 'Précipitations (mm)', 'fwi': 'Indice FWI', 'ndvi': 'NDVI',
}
KEY = ['cell_id', 'date']


def monthly_distributions(train, val):
    rows = []
    for cohort, frame in [('Train', train), ('Validation', val)]:
        for month, group in frame.groupby(frame.date.dt.month):
            for variable in MEASURES:
                values = group[variable]
                lower, median, upper = values.quantile([.25, .5, .75])
                rows.append(dict(cohort=cohort, month=month, variable=variable,
                                 n=len(group), positives=int(group.label.sum()),
                                 measured=values.count(), q25=lower, median=median, q75=upper))
    return pd.DataFrame(rows)


def align_scores(val, scores, model):
    """Vérifier les clés, dates, cibles et probabilités avant toute stratification."""
    keys = [*KEY, 'year', 'label']
    for frame in (val, scores):
        if (frame.empty or frame[keys].isna().any().any() or frame.duplicated(KEY).any()
                or not frame.year.eq(2024).all() or not frame.date.dt.year.eq(2024).all()
                or not frame.label.isin([0, 1]).all()):
            raise ValueError('Clés, dates ou cibles de validation invalides.')
    linked = val.merge(scores[[*keys, model]], on=keys, how='outer', validate='one_to_one',
                       indicator=True)
    if not linked['_merge'].eq('both').all() or not linked[model].between(0, 1).all():
        raise ValueError('Les prédictions et les observations de 2024 ne concordent pas.')
    return linked


def spatial_block(frame):
    # Coin sud-ouest du bloc de 1 degré, convention du benchmark exploratoire.
    return np.floor(frame.lat).astype(int).astype(str) + ':' + np.floor(frame.lon).astype(int).astype(str)


def error_profiles(train, linked, model, threshold):
    positive = linked.label.eq(1)
    alert = linked[model].ge(threshold)
    counts = pd.DataFrame({'tp': positive & alert, 'fn': positive & ~alert,
                           'fp': ~positive & alert, 'tn': ~positive & ~alert})
    groups = {'bloc_1_degre': spatial_block(linked)}
    for variable in MEASURES:
        # Les bornes viennent du train et les valeurs manquantes restent comptées.
        cuts = train[variable].quantile([.25, .5, .75]).dropna().unique()
        bins = pd.cut(linked[variable], bins=[-np.inf, *cuts, np.inf], precision=6)
        groups[variable] = bins.astype('string').fillna('Manquant')
    pieces = []
    for dimension, strata in groups.items():
        totals = counts.groupby(strata, observed=True).sum()
        totals.index.name = 'stratum'
        totals['n'] = totals.sum(axis=1)
        totals['recall'] = totals.tp.div((totals.tp + totals.fn).replace(0, np.nan))
        totals['precision'] = totals.tp.div((totals.tp + totals.fp).replace(0, np.nan))
        pieces.append(totals.assign(dimension=dimension).reset_index())
    return pd.concat(pieces, ignore_index=True)


def plot_months(table, path):
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.4), layout='constrained')
    for (cohort, color) in [('Train', '#21618c'), ('Validation', '#b44b21')]:
        rows = table.loc[table.cohort.eq(cohort)]
        for ax, (variable, title) in zip(axes.flat, MEASURES.items()):
            group = rows.loc[rows.variable.eq(variable)]
            ax.plot(group.month, group['median'], marker='.', color=color)
            ax.fill_between(group.month, group.q25, group.q75, color=color, alpha=.13)
            ax.set_title(title, fontsize=10)
        ax = axes.flat[-1]
        ax.set_title('Détections dans l’échantillon (%)', fontsize=10)
        ax.plot(group.month, 100 * group.positives / group.n, marker='.', color=color,
                label='Train 2012–2023' if cohort == 'Train' else 'Validation 2024')
        ax.legend(fontsize=8)
    for ax in axes.flat:
        ax.set_xticks(sorted(table.month.unique()))
        ax.set_xlabel('Mois')
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run(output):
    train, val, _, _, _ = development_inputs()
    frozen = json.loads((LOT / 'decision.json').read_text())
    model = frozen['model']
    scores = pd.read_csv(LOT / 'predictions_validation.csv', parse_dates=['date'])
    linked = align_scores(val, scores, model)
    months = monthly_distributions(train, val)
    errors = error_profiles(train, linked, model, frozen['threshold'])
    geography = []
    for cohort, frame in [('Train', train), ('Validation', val)]:
        totals = frame.groupby(spatial_block(frame)).label.agg(n='size', positives='sum')
        totals.index.name = 'bloc_1_degre'
        geography.append(totals.assign(cohort=cohort, fraction=totals.positives / totals.n))
    folder = new_output(output)
    pd.concat(geography).to_csv(folder / 'geographie.csv')
    months.to_csv(folder / 'distributions_mensuelles.csv', index=False)
    errors.to_csv(folder / 'erreurs_2024.csv', index=False)
    plot_months(months, folder / 'comparaison_mensuelle.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    run(parser.parse_args().output)
