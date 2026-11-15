# Extensions scientifiques SIAD03

Ce lot complète le dépôt sans modifier ses fichiers préexistants. Le rapport
`RAPPORT.md` et sa version PDF présentent les résultats exécutés, y compris les
résultats décevants. `AUDIT_PLAN.md` contient la conformité initiale et le Top 10.
Les nouveaux modèles ne remplacent aucun modèle obligatoire.

## Installation et reproduction

Depuis la racine du dépôt, avec Python 3.12 :

```sh
python -m venv .venv
# Linux/macOS : source .venv/bin/activate
# PowerShell : .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m src.siad03_extensions.exploration --output results/local_runs/eda_01
python -m src.siad03_extensions.benchmark --output results/local_runs/benchmark_01
python -m src.siad03_extensions.explain --benchmark results/local_runs/benchmark_01 --output results/local_runs/explain_01
python -m streamlit run src/siad03_extensions/dashboard.py
```

Les dossiers de sortie doivent être nouveaux : une relance ne remplace pas une
expérience antérieure. Les commandes résolvent les données à partir de la racine
du package ; les sorties relatives dépendent du dossier courant. Le dashboard
lit le lot versionné `results/siad03_extensions/benchmark`. Aucun entraînement
n'est lancé par l'interface. Les tests d'artefacts exigent ces résultats versionnés.
Les nouveaux modèles utilisent deux threads natifs, une graine 42 et n_jobs=1.
La durée exacte dépend du matériel ; les scores peuvent varier légèrement selon
les bibliothèques numériques. Installation testée avec les versions existantes.

Pour reconstruire le PDF (dépendance de publication uniquement) :

```sh
python -m pip install -r docs/siad03_extensions/requirements-report.txt
python -m src.siad03_extensions.report --output results/local_runs/rapport_SIAD03.pdf
```

## Intégration proposée

Le responsable de l'application peut importer
`render_scientific_dashboard` depuis `src.siad03_extensions.dashboard` dans une
page dédiée. Le module n'appelle `set_page_config` que lorsqu'il est lancé seul.
Les clés de widgets EDA existantes imposent de ne pas afficher deux fois `render_eda`
sur la même page. Les résultats ne doivent pas être présentés comme une validation finale.

Avant toute intégration collective : faire confirmer le protocole proposé, réentraîner
l'arbre avec la version commune, compléter K-NN/SVM/RF et le formulaire dans leurs
périmètres respectifs, contrôler la provenance, puis geler les choix avant 2025.
Ne charger que des artefacts joblib de confiance. Aucun fichier du socle n'a été changé.

## Fichiers nouveaux

|Chemin sous les dossiers d'extensions|Rôle|
|---|---|
|src/.../data.py|Lecture train/validation, empreintes, refus d'écrasement|
|src/.../evaluation.py|Métriques, calibration, erreurs, bootstrap par cellule|
|src/.../benchmark.py|Deux recherches exhaustives à cinq plis et comparaison de cinq modèles|
|src/.../exploration.py|Dénominateurs, cartes, saisons, dérive et reproduction statistique|
|src/.../explain.py|Permutations mensuelles et courbes de performance|
|src/.../dashboard.py|Page Streamlit indépendante|
|src/.../report.py|Construction reproductible du PDF depuis le rapport Markdown|
|tests/siad03_extensions/|Tests unitaires et d'intégration|
|results/.../benchmark/|Modèles, grilles, prédictions 2024, métriques et incertitude|
|results/.../exploration/|Agrégats train, statistiques et graphiques|
|results/.../explain/|Explications descriptives et courbes|
|results/.../verification/|Preuves des tests et protection des fichiers|
|docs/siad03_extensions/|Audit, guide, annexe scientifique et exigences de publication|

L'assistance IA a servi à l'audit, au développement, aux tests et à la rédaction.
SIAD03 doit relire les choix, savoir les expliquer à l'oral et valider l'intégration.
L'historique Git reflète les étapes réelles de cette intervention, pas un travail
antidaté. Aucun push, message à l'équipe ni fusion automatique n'a été effectué.
