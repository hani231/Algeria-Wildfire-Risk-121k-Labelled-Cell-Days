"""Analyses exploratoires par année, avec contrôle de la saison en sensibilité."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from src.cleaning_guide import clean_data

VARIABLES = ("temp_max", "rh_mean")


def holm_adjust(p_values):
    """Holm à famille fixe ; les tests non calculables restent NaN.

    Leur p-value vaut provisoirement 1 pour ne pas réduire artificiellement
    le nombre de tests de la famille prévue.
    """
    p = np.asarray(p_values, dtype=float)
    if np.isinf(p).any() or ((p < 0) | (p > 1)).any():
        raise ValueError('Une p-value doit être comprise entre 0 et 1.')
    if len(p) == 0:
        return p.copy()
    safe = np.where(np.isnan(p), 1.0, p)
    order = np.argsort(safe, kind='stable')
    adjusted = np.minimum(1.0, np.maximum.accumulate(
        safe[order] * np.arange(len(p), 0, -1)))
    result = np.empty_like(p)
    result[order] = adjusted
    result[np.isnan(p)] = np.nan
    return result


def analyse_training(df, match_month=False):
    """Retourner résultats, écarts annuels et nombres de zones appariées.

    L'analyse principale conserve l'appariement zone/année du notebook.
    La sensibilité compare d'abord les classes dans la même zone/année/mois,
    puis moyenne les mois par zone, les zones par année (poids égaux).
    Les années 2024 et 2025 sont exclues avant tout calcul statistique.
    """
    required = {'cell_id', 'date', 'year', 'label', 'split', *VARIABLES}
    if not required.issubset(df.columns):
        raise ValueError(f'Colonnes absentes : {sorted(required.difference(df.columns))}')
    train = df.loc[df['split'].eq('train')].copy()
    if train.empty:
        raise ValueError("Aucune donnée d'entraînement pour les analyses.")
    if not train['year'].between(2012, 2023).all():
        raise ValueError("Les analyses doivent rester dans l'entraînement 2012-2023.")
    dates = pd.to_datetime(train['date'], errors='raise')
    if not train['year'].eq(dates.dt.year).all():
        raise ValueError('Incohérence entre date et année.')
    if not train['label'].isin([0, 1]).all():
        raise ValueError('La cible doit valoir 0 ou 1.')
    if train.duplicated(['cell_id', 'date']).any():
        raise ValueError('Clés zone/jour répétées : nettoyer avant analyse.')
    train['month'] = dates.dt.month
    groups = ['year', 'cell_id'] + (['month'] if match_month else [])
    records, annual_values, counts = [], {}, {}
    for variable in VARIABLES:
        paired = (train.groupby(groups + ['label'])[variable].mean()
                  .unstack('label').reindex(columns=[0, 1]).dropna())
        gaps = paired[1] - paired[0]
        if match_month:
            gaps = gaps.groupby(level=['year', 'cell_id']).mean()
        annual = gaps.groupby(level='year').mean()
        annual_values[variable] = annual
        counts[variable] = gaps.groupby(level='year').size()
        nonzero = annual.loc[annual.ne(0)]
        n, k = len(nonzero), int(nonzero.gt(0).sum())
        result = binomtest(k, n, p=0.5, alternative='two-sided') if n else None
        ci = result.proportion_ci(method='exact') if result else None
        records.append({
            'variable': variable, 'annees_non_nulles': n, 'annees_ecart_positif': k,
            'ecart_annuel_moyen': annual.mean(), 'ecart_annuel_min': annual.min(),
            'ecart_annuel_max': annual.max(),
            'p_brute': result.pvalue if result else np.nan,
            'proportion_positive': k / n if n else np.nan,
            'ic95_proportion_bas': ci.low if ci else np.nan,
            'ic95_proportion_haut': ci.high if ci else np.nan,
            'annees_sans_paire': int(train.year.nunique() - len(annual)),
            'annees_ecart_nul': int(annual.eq(0).sum()),
        })
    summary = pd.DataFrame(records)
    summary['p_holm'] = holm_adjust(summary['p_brute'])
    return summary, pd.DataFrame(annual_values), pd.DataFrame(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('Dataset/dataset.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/audit_siad03'))
    args = parser.parse_args()
    df, _ = clean_data(pd.read_csv(args.data))
    args.output.mkdir(parents=True, exist_ok=True)
    for monthly, suffix in [(False, 'principal'), (True, 'sensibilite_mois')]:
        summary, gaps, counts = analyse_training(df, match_month=monthly)
        summary.to_csv(args.output / f'statistiques_{suffix}.csv', index=False)
        gaps.to_csv(args.output / f'ecarts_{suffix}.csv', index_label='annee')
        counts.to_csv(args.output / f'zones_{suffix}.csv', index_label='annee')
        print(suffix, summary[['variable', 'ecart_annuel_moyen', 'p_holm']].to_string(index=False))
    (args.output / 'methode_statistique.json').write_text(json.dumps({
        'population': 'train 2012-2023 uniquement',
        'h0': "P(écart annuel > 0 | écart non nul) = 0.5",
        'h1': "P(écart annuel > 0 | écart non nul) != 0.5",
        'test': 'binomial exact bilatéral sur les signes annuels',
        'correction': 'Holm, famille de deux tests par analyse',
        'sensibilite': 'zone/année/mois, exploratoire post hoc, ne remplace pas le principal',
        'limites': ['Indépendance des signes annuels non démontrée',
                    'Même mois ne garantit pas un appariement météorologique complet',
                    'Négatifs sélectionnés ; ni causalité ni risque absolu',
                    'IC sur la proportion de signes positifs, pas sur la taille de l’effet'],
    }, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
