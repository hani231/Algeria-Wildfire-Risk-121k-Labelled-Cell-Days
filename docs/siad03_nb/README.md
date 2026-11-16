# Expériences reproductibles Zero-R et GaussianNB — SIAD03

Cette contribution complète les notebooks et l'extension scientifique déjà intégrés.
Elle n'altère aucun fichier préexistant. Le protocole est lu, vérifié, jamais réécrit.

## Exécution depuis la racine

Python 3.12 et dépendances existantes `requirements-dev.txt`. Dans l'environnement
cloud préparé : `source /workspace/.venvs/wildfire/bin/activate`.
Pour un autre poste : créer un venv puis `python -m pip install -r requirements-dev.txt`.

```sh
python -m pytest -q
python -m src.siad03_nb.experiment --output results/local_runs/nb_01
python -m src.siad03_nb.diagnostics --experiment results/local_runs/nb_01 --output results/local_runs/nb_01_figures
```

Les dossiers de sortie doivent être neufs ; les artefacts versionnés ne sont pas écrasés.
L'expérience a pris environ 21 secondes sur la machine de validation (durée indicative),
avec deux threads natifs et un seul job CV. Elle utilise 104 979 lignes train, 8 423
lignes de validation et 24 prédicteurs. Aucune nouvelle dépendance n'est nécessaire.

La grille comprend les puissances de dix de 10^-12 à 10^1 (14 configurations), choisies
avant l'exécution. Les cinq plis annuels valident 2019–2023. La sélection maximise le
F1 de classe 1 moyen ; le seuil demeure 0,5. Zero-R n'a aucun hyperparamètre optimisé.
`var_smoothing` stabilise les variances gaussiennes : ce n'est pas le lissage de Laplace.
`keep_empty_features=True` conserve les dimensions si une variable est totalement
manquante dans un pli, sans apprendre une médiane à partir de sa validation.

Le CSV est lu pour identifier les partitions ; les lignes `test` sont exclues avant
nettoyage et calculs de développement. Le SHA-256 couvre le fichier brut entier pour
la provenance : il ne constitue pas une évaluation de 2025.

## Sorties et intégration

Le lot exécuté est dans `results/siad03_nb/run_01` : grilles complètes, scores par pli,
prédictions 2024, métriques, erreurs mensuelles, calibration, modèles et provenance.
Les figures sont dans `results/siad03_nb/figures`. `provenance.json` contient le commit
présent au démarrage et les empreintes exactes des sources utilisées, y compris lorsqu'une
source était en cours de préparation. Les durées varient entre exécutions.

Les résultats ne remplacent pas `results/protocole_propose.json` ni les artefacts
communs de `models/`. Pour intégrer, le responsable du protocole doit confirmer le
contrat actuel ; l'intégrateur choisit ensuite la présentation collective. Ne pas
brancher automatiquement ces modèles sur le formulaire sans cette validation.

Voir [l'audit comparatif](AUDIT.md) et [les résultats scientifiques](RESULTATS.md).
Les anciens notebooks et le tableau de bord sont conservés ; les tests complets
incluent leurs modules et les interactions des deux vues EDA.
