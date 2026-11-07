# Implémentation de l'Arbre de décision

## Protocole de travail partagé

Le dataset nettoyé contient 104 979 lignes d'entraînement de 2012 à 2023,
8 423 lignes de validation en 2024 et 8 467 lignes de test en 2025.
Le test 2025 reste réservé et ne sert ni au réglage, ni à la sélection du modèle.

Le notebook Zero-R / Naïve Bayes construit cinq plis temporels croissants :
entraîner jusqu'en 2018 puis valider en 2019, jusqu'en 2019 puis valider en 2020,
et ainsi de suite jusqu'à entraîner jusqu'en 2022 puis valider en 2023.
Le fichier `results/plis_temporels.csv` documente les tailles exactes.
Ces plis et le F1 de la classe 1 sont une **proposition à confirmer avec Hani**;
le script affiche un avertissement tant que le protocole n'est pas marqué confirmé.

## Entraîner le modèle

Depuis la racine du dépôt, avec pandas, NumPy, scikit-learn et joblib installés :

```bash
python -m src.train_decision_tree
```

Le script lit les variables et les années de validation de
`results/protocole_propose.json`, impute les valeurs manquantes par la médiane
dans chaque pli, et règle l'arbre par GridSearchCV sur le F1. L'arbre n'est pas
standardisé. Sa grille compare Gini/entropie, plusieurs profondeurs, tailles
minimales de feuille et l'utilisation éventuelle de poids équilibrés.

Les résultats sont enregistrés dans :

- `results/recherche_arbre_decision.csv` : tous les réglages et leurs scores CV ;
- `results/resultats_arbre_decision_validation.csv` : comparaison CV et validation 2024 ;
- `models/arbre_decision_developpement.joblib` : pipeline entraîné sur tout le train 2012–2023.

Les scores sont provisoires jusqu'à confirmation par l'équipe. Le rapport final devra
comparer tous les modèles avec les mêmes variables, plis, métriques et partitions.
L'artefact généré ici utilise scikit-learn 1.9.1, tandis que les résultats des notebooks
existants ont été calculés avec 1.8.0. Avant de charger ces modèles ensemble dans l'application,
alignez la version scikit-learn et réentraînez les modèles si nécessaire.
