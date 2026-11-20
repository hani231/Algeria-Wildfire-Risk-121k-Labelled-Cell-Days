# Algeria Wildfire Risk — classification de cellules-jours

Projet universitaire de fouille de données : étudier les liens entre météo, végétation et détections d'incendie en Algérie.

**Wildfire Atlas** réunit six espaces Streamlit pour explorer les observations, comparer cinq classifieurs documentés et interroger quatre pipelines compatibles. K-NN, Random Forest et SVM restent à intégrer au benchmark. [Lancement et captures de l’interface](docs/INTERFACE.md)

## 1. Objectifs et données

Une ligne correspond à une zone (`cell_id`) et une date. `label=1` indique une détection ; `label=0` son absence dans le fichier, sans prouver l'absence de feu réel. Les négatifs sont sélectionnés : les proportions ne mesurent pas le risque territorial. La météo du jour sert à une **classification rétrospective**, pas à une prévision opérationnelle.

Source annoncée : [Kaggle](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days). Le brut `Dataset/dataset.csv`, environ 45,5 Mo, est récupéré par le clone. La version producteur, la licence, certaines unités et la construction historique des variables restent à documenter.

| Propriété vérifiée | Valeur |
|---|---:|
| Lignes / colonnes brutes | 121 869 / 37 |
| Zones | 1 423 |
| Colonnes après retrait des trois fuites | 34 |
| Train 2012–2023 | 104 979 lignes |
| Validation 2024 | 8 423 lignes |
| Test réservé 2025 | 8 467 lignes |

Les 24 entrées proposées figurent dans `results/protocole_propose.json`. `sample_kind`, `n_detections`, `max_frp`, `label` et `split` sont interdits comme prédicteurs. `days_since_last_fire`, `ndvi_normal` et `ndvi_anomaly` sont provisoirement exclus, en attendant la vérification de leur construction. Les NaN sont imputés dans chaque pli, au sein des pipelines. Lire le [dictionnaire](docs/dictionnaire_colonnes.md).

## 2. Installation et exécution locale

Environnement du lot SIAD03 : **Python 3.12.14**, scikit-learn **1.8.0**. L'ancien artefact de l'arbre utilise **1.9.1** : le réentraîner dans l'environnement commun avant intégration. Un chargement sans crash ne garantit pas la compatibilité.

Sous PowerShell :

```powershell
git clone https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days.git
cd Algeria-Wildfire-Risk-121k-Labelled-Cell-Days
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.audit_data
.\.venv\Scripts\python.exe -m src.verify_existing
.\.venv\Scripts\python.exe -m src.statistical_analysis
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```

Sous Linux/macOS : créer l'environnement avec `python3.12 -m venv .venv`, puis employer `.venv/bin/python` à la place de `.\.venv\Scripts\python.exe`.

L'audit écrit dans `results/audit_siad03/` et conserve le brut. La démo propose statistiques, manquants, histogramme/KDE, boxplot, fréquences, corrélation et filtres années/classes/mois/zones. Elle utilise uniquement le train. L'histogramme utilise au plus 5 000 valeurs ; les tableaux et boxplots utilisent tout le filtre. Une sélection vide affiche un message.

### Notebooks et entraînement

Dans VS Code, installer les extensions Python/Jupyter et choisir le noyau `.venv`. Exécuter toutes les cellules de `notebooks/01_eda_and_cleaning.ipynb`, puis de `notebooks/03_zeror_naive_bayes.ipynb`. Le second entraîne Zero-R et GaussianNB. Les notebooks réécrivent des fichiers suivis : convenir d'un intégrateur avant une relance sur une branche commune.

L’archive fournie rapporte une exécution historique de 21 cellules Python dans une copie isolée. Les notebooks n’ont pas été réexécutés pendant cette intégration ; leur lancement dans Jupyter reste à vérifier.

L'arbre dispose de la commande existante suivante, après harmonisation des versions et du protocole :

```powershell
.\.venv\Scripts\python.exe -m src.train_decision_tree
```

Le notebook historique recherche 7 valeurs de `var_smoothing`, l'arbre 48 combinaisons. Les cinq plis valident 2019 à 2023, en apprenant sur les années précédentes. Le F1 de classe 1 est la métrique de sélection proposée. Cette validation chronologique diffère d'un K-Fold classique : acceptation pédagogique à confirmer. **2025 reste réservé** jusqu'au gel des choix.

| Chemin | Rôle |
|---|---|
| `Dataset/dataset.csv` | Brut versionné |
| `Dataset/processed.csv` | Ancien export intermédiaire ; ne pas utiliser comme brut |
| `data/processed/dataset_clean.csv` | Données nettoyées non imputées |
| `notebooks/` | EDA/nettoyage, Zero-R/NB |
| `src/cleaning_guide.py`, `src/data_quality.py` | Nettoyage et contrôles |
| `src/audit_data.py`, `src/statistical_analysis.py` | Audits et analyses reproductibles |
| `src/app.py`, `src/ui/` | Navigation, cartes, présentation scientifique et intégration des modèles |
| `src/eda_view.py`, `src/run_eda_demo.py` | Vue intégrable et démo |
| `src/train_decision_tree.py` | Recherche et entraînement arbre |
| `models/`, `results/`, `figures/` | Artefacts, métriques, figures |
| `tests/` | Nettoyage, statistiques, interactions EDA |
| `docs/` | Dictionnaire, audit, guides ; rapport final absent |

`src/preprocessing.py`, `src/models.py`, les notebooks communs et `docs/Rapport_MiniProject.pdf` restent à intégrer.

## 3. Rôles et contributions

| Code | Responsabilités | Preuves présentes |
|---|---|---|
| SIAD03, confirmé | Données, nettoyage, EDA, statistiques, Zero-R/NB, interface Wildfire Atlas | Notebooks 01/03, scripts, résultats ; six espaces Streamlit et tests |
| IASD12, code historique à confirmer | Protocole, prétraitement, K-NN/SVM, consolidation | Initialisation et ancien notebook dans l'historique ; modèles absents au HEAD |
| IASD17, code historique à confirmer | Arbre/RF, application, assemblage | Script et résultats de l'arbre ; RF en attente |

Chaque auteur doit comprendre, tester et commiter son travail. Aucun historique n'est antidaté ou réattribué. Des supports anciens contiennent encore des identités : les anonymiser avant le rendu public, en conservant les originaux internes.

## 4. Résultats vérifiés et limites

Scores recalculés à partir des artefacts sur la **validation 2024**, pas sur le test final.

| Modèle | Accuracy | Précision 1 | Rappel 1 | F1 1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Zero-R | 0,9237 | 0,0000 | 0,0000 | 0,0000 | 0,5000 |
| GaussianNB (run_01) | 0,5060 | 0,0995 | 0,6796 | 0,1736 | 0,6314 |
| LogisticRegression (supplémentaire) | 0,6006 | 0,1094 | 0,5925 | 0,1847 | 0,6355 |
| HistGradientBoosting (supplémentaire) | 0,6418 | 0,1017 | 0,4712 | 0,1673 | 0,6207 |
| DecisionTree | 0,5572 | 0,0958 | 0,5692 | 0,1641 | 0,6092 |
| K-NN | — | — | — | — | — |
| Random Forest | — | — | — | — | — |
| SVM | — | — | — | — | — |

Zero-R prédit toujours 0 et rate les 643 positifs ; précision à 0 par convention. Le GaussianNB présenté dans l’application retrouve 437 détections avec 3 955 faux positifs. Son F1 est 0,17358490566037735 pour le lot run_01 (14 réglages, var_smoothing = 1). Le benchmark historique utilise 7 réglages et obtient 0,17668110755321154. Le lot courant a été choisi pour sa traçabilité, avec sélection sur les cinq plis du train. L'arbre en retrouve 366 avec 3 453 faux positifs. Ces performances sont conservées et discutées.

Les deux analyses principales utilisent les écarts annuels après appariement zone/année. Effets moyens : **+3,0769 unités CSV** de température et **−10,1067 points d'humidité**. Le complément zone/année/mois donne **+2,3071** et **−9,5909**. Chaque p-value principale ajustée par Holm vaut **0,0009765625**. L'indépendance des signes annuels n'est pas démontrée : résultats exploratoires, sans causalité ni risque absolu. L'audit détaille H0/H1 et les limites.

Les probabilités ne sont pas certifiées calibrées. Des variables disponibles après la journée empêchent de présenter le projet comme une alerte anticipée.

Références : [validation scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html), [test binomial SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html), [tests Streamlit](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [cahier des charges](https://hosniadilemp-a11y.github.io/DataMiningProjectPage/).

## Vérification de cette intégration

Depuis la racine, lancer `python -m pytest -q`. Les tests d’interface exercent les six espaces, les quatre pipelines compatibles, les filtres et les résultats versionnés. Les tests de qualité comparent les matrices sur 2024 et vérifient les saisies invalides. Les documents des premiers lots décrivent leur état à la date de rédaction.

[Contribution scientifique SIAD03](docs/contributions/SIAD03.md) · [Matrice de conformité](docs/MATRICE_CONFORMITE.csv)
