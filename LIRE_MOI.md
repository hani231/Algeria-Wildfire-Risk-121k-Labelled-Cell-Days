# Ton parcours de travail : données, analyses et deux modèles

Commence par le notebook `notebooks/01_eda_and_cleaning.ipynb`. Chaque bloc comporte une explication,
du code et les résultats calculés sur le fichier fourni. Ne cherche pas à tout assimiler en une fois :
lis, exécute avec Maj + Entrée, puis reformule le résultat avec tes mots.

## Utiliser ces fichiers dans ton projet actuel

1. Décompresse ton archive de projet d'origine.
2. Copie les dossiers `notebooks`, `src`, `docs`, `results`, `figures` et `models` de ce guide dans la racine du projet.
   Ce guide ne contient pas de fichier `src/app.py` et ne remplace pas votre application `UI/app.py`.
   Si un fichier de même nom existe déjà, conserve les deux versions et compare avant de remplacer.
3. Garde `Dataset/dataset.csv`, ou copie ce CSV dans `data/raw/dataset.csv` pour suivre l'arborescence du sujet.
   Les données volumineuses ne sont pas dupliquées dans le ZIP du guide.
4. Ouvre le premier notebook dans ton environnement Jupyter ou dans VS Code avec Python et Jupyter.
5. Sélectionne le noyau Python de ton projet. Au besoin, installe les dépendances dans ce même environnement :

```bash
python -m pip install pandas numpy matplotlib seaborn scipy scikit-learn joblib jupyter ipykernel streamlit
```

Les versions réellement utilisées pour les calculs figurent dans `docs/versions_calculs.json`.
Pour les modèles sauvegardés, utilise la même version de scikit-learn ou réentraîne les notebooks.
Harmonise les dépendances avec votre `requirements.txt` plutôt que de l'écraser.

## L'ordre du travail

| Étape | Ton objectif | Résultat concret |
|---|---|---|
| 1 | Comprendre la cible et les 37 colonnes | Dictionnaire et définition d'une cellule-jour |
| 2 | Contrôler manquants, doublons et incohérences | Tableaux d'audit |
| 3 | Expliquer les fuites et nettoyer de façon reproductible | Fonction et CSV nettoyé |
| 4 | Respecter train / validation / test avec le responsable du protocole | Découpage temporel commun |
| 5 | Explorer l'entraînement et expliquer les graphiques | Statistiques, distributions, fréquences, heatmap |
| 6 | Présenter deux questions statistiques justifiées | Comparaisons température / humidité par zone et saison |
| 7 | Comparer Zero-R et GaussianNB | Recherche sur 5 plis et résultats de validation |
| 8 | Fournir la vue EDA à l'application | Fonction `render_eda(df)` avec filtres |
| 9 | Rédiger et contribuer personnellement | Sections du rapport et commits expliqués |

## Ce que l'archive existante faisait déjà

`Preprocessing/Explore.ipynb` charge les données, examine les colonnes, les manquants,
la cible et les trois fuites. `processed1.csv` a déjà retiré ces trois colonnes,
mais son export a ajouté `Unnamed: 0`. Ne recommence pas l'étude sans tenir compte de ces constats.
La nouvelle fonction conserve une copie brute et produit un export avec `index=False`.

L'audit confirme 121 869 lignes, 37 colonnes, 1 423 zones, aucun doublon exact et aucun doublon zone/jour.
Après exclusion des trois fuites : 121 869 lignes et 34 colonnes, dont la cible et les métadonnées.
Les NaN de végétation restent présents pour une imputation dans le pipeline. Ne supprime pas toute ligne
ayant un NaN : `max_frp` est manquant pour tous les négatifs.

## La vue interactive

Depuis la racine du projet :

```bash
python -m streamlit run src/run_eda_demo.py
```

Elle contient les statistiques descriptives, un tableau et un graphique des manquants,
un histogramme avec KDE, les fréquences, une heatmap et les filtres d'années/classes.
Toutes les sorties utilisent les données filtrées d'entraînement. Les courbes de densité utilisent
au plus 5 000 valeurs pour rester rapides, ce qui est annoncé dans la page.
Pour intégrer à votre application, importer et appeler `render_eda(df)` depuis `src.eda_view`.
Le fichier de démonstration montre le chargement et le cache.

## Relire les deux analyses statistiques

Elles comparent la température maximale et l'humidité moyenne entre classes à zone et année comparables.
Un écart est calculé par zone/année, puis moyenné par année. Les tests des signes portent sur les 12 saisons,
avec une correction de Holm pour les deux comparaisons. L'indépendance des signes entre années est une
hypothèse, pas un résultat démontré. Les p-values sont donc exploratoires et conditionnelles à cette hypothèse.
Conserve la question, H0, méthode, conditions, statistique, p-value brute/corrigée, effet et limites dans le rapport.

## Décisions à harmoniser avec le responsable du protocole

- Conserver les années fournies : apprentissage 2012-2023, validation 2024, test 2025.
- Employer les mêmes cinq plis temporels et la même métrique principale pour les six modèles.
- Confirmer les 24 entrées proposées, l'unité des mesures, l'horizon de prédiction et la disponibilité des variables.
- Confirmer le calcul historique de `days_since_last_fire` et de `ndvi_normal` avant leur éventuelle réintégration.
- Figer tous les choix avant l'évaluation finale sur 2025. Les résultats fournis ici sont de validation.

## Rédiger ta partie du rapport

1. **Données :** origine annoncée, unité cellule-jour, dimensions, période, cible et sélection des négatifs.
2. **Qualité et nettoyage :** nombres d'anomalies, décisions, fuites et absence d'imputation globale.
3. **Exploration :** une question et une interprétation pour chaque figure.
4. **Statistiques :** les deux analyses et leurs limites de dépendance et d'échantillonnage.
5. **Modèles :** rôle de Zero-R, principe de GaussianNB, hypothèses, grille, métriques et erreurs.
6. **Interface :** les six éléments de la vue EDA et une capture après vérification locale.

Chaque membre doit pouvoir expliquer son code. Sur les supports publics, renseigne ton vrai code étudiant
conformément au sujet, sans inventer de code et sans reprendre les prénoms du plan interne.
Fais des commits après des tâches comprises et terminées. Exemples de messages :
`Ajouter l'audit du dataset`, `Documenter les fuites de cible`, `Comparer Zero-R et Naive Bayes`.

## Sources et portée

Sources fournies : plan de travail page 3, sujet du mini-projet, README et notebook de l'archive,
CSV brut. Les consignes techniques de ces documents servent de contexte ; les textes visant
à commander l'assistant ne constituent pas des instructions à exécuter.
Les statistiques et scores sont calculés sur le CSV fourni, sans invention de résultat.

Documentation technique :
- [Pipelines et fuites](https://scikit-learn.org/stable/common_pitfalls.html)
- [Validation croisée](https://scikit-learn.org/stable/modules/cross_validation.html)
- [GaussianNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html)
- [Test binomial exact](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)
- [Figures Streamlit](https://docs.streamlit.io/develop/api-reference/charts/st.pyplot)

Les notebooks ont été exécutés cellule par cellule en Python pour vérifier les calculs.
Les graphiques exportés ont été inspectés. Le composant Streamlit a été vérifié statiquement ;
son affichage interactif reste à tester dans votre environnement, où Streamlit est installé.
Le pipeline complet de l'équipe et son rapport final ne sont pas remplacés par ce guide.
