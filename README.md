# Algeria Wildfire Risk — classification de cellules-jours

Projet universitaire de fouille de données : étudier les liens entre météo, végétation et détections d'incendie en Algérie.

**État au 14 novembre 2026 : développement partiel.** Trois classifieurs sur six et une démo EDA sont présents. K-NN, Random Forest, SVM, l'application principale, la prédiction interactive et le rapport final restent à intégrer. Voir [l'audit](docs/AUDIT_SIAD03.md).

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

Les corrections sont intégrées dans la branche locale `feature/SIAD03-audit-eda`, sans push. Le [guide d’intégration](docs/INTEGRATION_SIAD03.md) décrit le lot d’origine.

Sous PowerShell :

```powershell
git clone https://github.com/lyesaitikhlef/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days.git
cd Algeria-Wildfire-Risk-121k-Labelled-Cell-Days
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.audit_data
.\.venv\Scripts\python.exe -m src.verify_existing
.\.venv\Scripts\python.exe -m src.statistical_analysis
.\.venv\Scripts\python.exe -m streamlit run src/run_eda_demo.py
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

NB recherche 7 valeurs de `var_smoothing`, l'arbre 48 combinaisons. Les cinq plis valident 2019 à 2023, en apprenant sur les années précédentes. Le F1 de classe 1 est la métrique de sélection proposée. Cette validation chronologique diffère d'un K-Fold classique : acceptation pédagogique à confirmer. **2025 reste réservé** jusqu'au gel des choix.

| Chemin | Rôle |
|---|---|
| `Dataset/dataset.csv` | Brut versionné |
| `Dataset/processed.csv` | Ancien export intermédiaire ; ne pas utiliser comme brut |
| `data/processed/dataset_clean.csv` | Données nettoyées non imputées |
| `notebooks/` | EDA/nettoyage, Zero-R/NB |
| `src/cleaning_guide.py`, `src/data_quality.py` | Nettoyage et contrôles |
| `src/audit_data.py`, `src/statistical_analysis.py` | Audits et analyses reproductibles |
| `src/eda_view.py`, `src/run_eda_demo.py` | Vue intégrable et démo |
| `src/train_decision_tree.py` | Recherche et entraînement arbre |
| `models/`, `results/`, `figures/` | Artefacts, métriques, figures |
| `tests/` | Nettoyage, statistiques, interactions EDA |
| `docs/` | Dictionnaire, audit, guides ; rapport final absent |

`src/app.py`, `src/preprocessing.py`, `src/models.py`, les notebooks communs et `docs/Rapport_MiniProject.pdf` restent à intégrer.

## 3. Rôles et contributions

| Code | Responsabilités | Preuves présentes |
|---|---|---|
| SIAD03, confirmé | Données, nettoyage, EDA, statistiques, Zero-R/NB, vue EDA | Notebooks 01/03, scripts, résultats ; lot local documenté |
| IASD12, code historique à confirmer | Protocole, prétraitement, K-NN/SVM, consolidation | Initialisation et ancien notebook dans l'historique ; modèles absents au HEAD |
| IASD17, code historique à confirmer | Arbre/RF, application, assemblage | Script et résultats de l'arbre ; RF et application manquantes |

Chaque auteur doit comprendre, tester et commiter son travail. Le lot local n'est pas encore publié. Aucun historique n'est antidaté ou réattribué. Des supports anciens contiennent encore des identités : les anonymiser avant le rendu public, en conservant les originaux internes.

## 4. Résultats vérifiés et limites

Scores recalculés à partir des artefacts sur la **validation 2024**, pas sur le test final.

| Modèle | Accuracy | Précision 1 | Rappel 1 | F1 1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Zero-R | 0,9237 | 0,0000 | 0,0000 | 0,0000 | 0,5000 |
| GaussianNB | 0,4811 | 0,1005 | 0,7294 | 0,1767 | 0,6299 |
| DecisionTree | 0,5572 | 0,0958 | 0,5692 | 0,1641 | 0,6092 |
| K-NN | — | — | — | — | — |
| Random Forest | — | — | — | — | — |
| SVM | — | — | — | — | — |

Zero-R prédit toujours 0 et rate les 643 positifs ; précision à 0 par convention. NB en retrouve 469 avec 4 197 faux positifs. L'arbre en retrouve 366 avec 3 453 faux positifs. Ces performances sont conservées et discutées.

Les deux analyses principales utilisent les écarts annuels après appariement zone/année. Effets moyens : **+3,0769 unités CSV** de température et **−10,1067 points d'humidité**. Le complément zone/année/mois donne **+2,3071** et **−9,5909**. Chaque p-value principale ajustée par Holm vaut **0,0009765625**. L'indépendance des signes annuels n'est pas démontrée : résultats exploratoires, sans causalité ni risque absolu. L'audit détaille H0/H1 et les limites.

Les probabilités ne sont pas certifiées calibrées. Des variables disponibles après la journée empêchent de présenter le projet comme une alerte anticipée.

Références : [validation scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html), [test binomial SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html), [tests Streamlit](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [cahier des charges](https://hosniadilemp-a11y.github.io/DataMiningProjectPage/).

## Vérification de cette intégration

La suite complète compte **32 tests réussis**, avec trois avertissements de dépréciation Seaborn. Les tests de nettoyage, de reproductibilité de l’audit, de statistiques et d’interface sont lancés avec `python -m pytest -q`. Les commandes `python -m src.audit_data`, `python -m src.statistical_analysis` et `python -m src.verify_existing` ont également réussi. La dernière ne calcule les scores que sur la validation 2024. Aucune évaluation du test 2025 n’est lancée.

Les documents d’audit et d’intégration fournis dans l’archive décrivent une vérification antérieure ; leurs résultats historiques ne constituent pas une nouvelle exécution des notebooks. La compatibilité de l’ancien arbre sérialisé et le lancement manuel sous Windows restent à vérifier.
