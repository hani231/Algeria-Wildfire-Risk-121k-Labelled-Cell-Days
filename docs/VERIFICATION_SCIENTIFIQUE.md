# Recette indépendante du protocole et des artefacts

## Sources pédagogiques et périmètre

La grille attribue 10 points au Data Mining, 4 à l’application, 3 à Git et 3 au rapport et au README. Le projet exemple met en œuvre GridSearchCV avec StratifiedKFold à cinq plis sur des observations cliniques. Son rapport associe théorie, validation, erreurs et application. Pour Atlas, l’unité est la cellule-jour avec récurrence des cellules entre années. Apprendre sur des années futures lors d’un mélange des lignes change la question expérimentale. Le professeur doit encore confirmer le choix principal chronologique. Les deux dépôts fournis donnent le cahier, sa page et l’exemple. Aucun support de cours distinct n’y était identifiable. [Cahier examiné](https://github.com/hosniadilemp-a11y/DataMiningProjectPage/blob/e3a19efa610228e3d7615cc8182f6a097db820ab/mini_project_proposal.pdf) · [Protocole de l’exemple](https://github.com/hosniadilemp-a11y/DataMiningProjectExample/blob/9c0551992df1b32034446a25abeb6ea781574338/src/models.py) · [Rapport de l’exemple](https://github.com/hosniadilemp-a11y/DataMiningProjectExample/blob/9c0551992df1b32034446a25abeb6ea781574338/docs/Rapport_MiniProject.pdf)

## Exécutions en copies isolées

| Vérification | Observations |
|---|---|
| Clone propre du main collectif da93591, installation de requirements-dev.txt dans un venv Python 3.12.14 neuf | pip check valide les dépendances. 109 tests réussis en 20,14 s sous Linux. |
| Branche IASD17 au commit 56c9285, avant corrections, autre copie | 169 tests réussis en 29,75 s sous Linux. Le passage des tests initiaux ne garantissait pas toutes les propriétés scientifiques de SHAP ou du CSV. |
| Nettoyage à partir du brut | SHA-256 du CSV cc260f954f76651c745c688c51e962a5fdbc4ee92d487ecd5577ba2aff7ecc26. src.verify_existing retrouve la table nettoyée complète, les cinq effectifs annuels et les scores 2024 de trois modèles historiques. |
| Statistiques appariées | Les sept fichiers reconstruits par src.statistical_analysis concordent octet pour octet avec results/audit_siad03. |
| Quatre notebooks communs 01, 02 et les deux 03 | Exécution nbclient dans une copie isolée avec noyau scikit-learn 1.8.0. 12, 2, 2 et 9 cellules de code exécutées respectivement pour nettoyage, préparation, comparaison et Zero-R/NB. |
| Deux notebooks secondaires 04_knn et acp | Exécution dans un noyau séparé scikit-learn 1.9.0, 21 et 13 cellules de code. Le noyau Jupyter a signalé le transport TCP local. Les notebooks préparent aussi les entrées du split test. La prédiction et l’AP de comparaison portent sur la validation. |
| Objet ACP/K-NN publié | Chaîne imputer, scaler, pca_95, knn_pca_95 rechargée séparément depuis le clone de base puis appliquée à 8 423 lignes de 2024. AP 0,105224847886, 25 variables, 12 composantes et 2 001 voisins. |
| Huit modèles disponibles dans l’application | 15 tests de test_final_benchmark.py réussis sous Linux, dont les deux nouveaux contrôles de la régression logistique et du gradient boosting. Contrôle de l’ordre des clés, des paramètres sauvegardés, des scores et des métriques de 2024. |
| Portabilité | La CI lance l’installation, pip check et pytest sur ubuntu-latest et windows-latest. La recette exécutée ici porte sur Linux. Le résultat hébergé pour chaque OS doit être lu sur la version soumise. |

La lecture du résultat 2025 utilise les prédictions déjà versionnées. Le programme de recette travaille en copie temporaire, car src.verify_existing écrit un JSON et plusieurs notebooks écrivent des figures ou des objets. Le contrôle de l’ancien arbre historique retrouve les valeurs 2024 mais relève des avertissements scikit-learn lors de la lecture d’objets 1.9.1 en 1.8.0. Le registre actif utilise l’arbre du benchmark commun. [Contrôle des huit modèles](../tests/test_final_benchmark.py) · [Registre](../src/ui/services.py)

Depuis la racine d’un clone de vérification à la révision souhaitée, utiliser un dossier de sortie neuf pour les statistiques.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest -q
python -m src.verify_existing
python -m src.statistical_analysis --output results/local_runs/stats_verifiees
```

Pour les notebooks 01 à 03, sélectionner ce noyau et les exécuter depuis notebooks/. Pour 04_knn et acp, utiliser la copie et le noyau 1.9.0 décrits dans l’audit antérieur, puis exécuter les cellules dans l’ordre original. [Environnement secondaire](AUDIT_REEVALUATION.md)

## Ce que comparent les F1

Pour les six modèles requis, la première paire ci-dessous est la moyenne sur cinq plis mélangés à paramètres gelés. La colonne chronologique est le F1 moyen sur les seules années de validation interne 2019 à 2023. Le dernier F1 est calculé au seuil 0,50 sur 2024. Les temps désignent le dernier ajustement et la prédiction sur la cohorte 2024, tels qu’enregistrés à l’époque de l’expérience.

| Modèle | KFold apprentissage | KFold validation | Chronologique validation | Validation 2024 | Ajustement / prédiction (s) |
|---|---:|---:|---:|---:|---:|
| Zero-R | 0,000 | 0,000 | 0,000 | 0,000 | 0,232 / 0,002 |
| GaussianNB | 0,507 | 0,507 | 0,410 | 0,174 | 0,263 / 0,003 |
| Arbre | 0,552 | 0,541 | 0,425 | 0,160 | 1,908 / 0,005 |
| Forêt | 0,600 | 0,563 | 0,430 | 0,167 | 13,184 / 0,029 |
| K-NN | 0,516 | 0,443 | 0,386 | 0,126 | 0,028 / 0,368 |
| SVM | 0,317 | 0,301 | 0,412 | 0,123 | 0,931 / 0,262 |

Zero-R manque toutes les détections. Le K-NN présente le plus grand écart entre apprentissage et validation mélangée dans ce tableau. Le SVM illustre que mélanger les années ne conduit pas systématiquement à un score supérieur. Le K-NN apprend sur 12 000 lignes et le SVM sur 3 500, contre 104 979 pour les quatre autres modèles lors de l’ajustement final. Une comparaison entre familles dépend donc aussi du budget. Les conclusions sur le sous-apprentissage et le surapprentissage doivent tenir compte du changement de saison, de la fréquence de la classe et des plafonds. [Métriques et temps](../results/benchmark_final/metrics.csv) · [Scores par pli](../results/post_freeze/kfold_train/folds.csv) · [Expérience de taille](../results/post_freeze/size_2024)

La régression logistique et HistGradientBoosting ont un lot séparé. Sur leurs meilleurs réglages chronologiques, les F1 moyens apprentissage/validation sont 0,579/0,426 et 0,627/0,436. Sur 2024 au seuil 0,50, leurs F1 sont 0,185 et 0,167. La recherche complète dure 16,67 et 41,23 s et la prédiction 0,003 et 0,019 s respectivement. Les durées d’ajustement moyen par pli au meilleur réglage sont 0,508 et 0,680 s. Leurs scores proviennent de la même cohorte vérifiée. [Recherches et résultats](../results/siad03_extensions/benchmark)

## Hypothèses statistiques et provenance de l’expérience secondaire

L’unité d’inférence du test des signes est l’année. Dans les cellules observées dans les deux classes, on calcule un écart de moyennes entre jours avec et sans détection, puis la moyenne annuelle des écarts par cellule. Sous H0, un écart annuel non nul est positif avec probabilité 0,5. L’alternative est bilatérale. Le signe évite de supposer normales les amplitudes de douze écarts. Les douze années donnent une température maximale plus élevée et une humidité plus basse les jours positifs. Les écarts moyens sont +3,077 °C et −10,107 points d’humidité. Pour chaque test, p brute = 0,00048828125 et p corrigée de Holm = 0,0009765625. L’appariement supplémentaire sur le mois utilise les mêmes observations. Les années peuvent être dépendantes, les témoins ont été sélectionnés et ces associations ne démontrent pas de causalité. [Méthode et sorties](../results/audit_siad03/methode_statistique.json)

Le commit 39531eb introduit les deux notebooks secondaires et quatre objets sous models/. L’historique les attribue à un autre contributeur que SIAD03 et que l’auteur de la branche IASD17. Le code étudiant de l’auteur est à confirmer par l’équipe. Le schéma à 25 entrées inclut ndvi_normal. Dans le dépôt du producteur, la climatologie utilise 2000–2011 et le code vérifie que cette fenêtre précède les années modélisées. Les dates des composites et un manifeste reliant chaque valeur au calcul amont manquent dans le CSV local. La provenance est donc plausible, avec une traçabilité par ligne incomplète. La comparaison avec les 24 entrées officielles demanderait le même budget, un pipeline unique et une recherche limitée aux plis du train. Les essais successifs de voisins et de variance retenue sur la même validation 2024 rendent l’écart d’AP exploratoire. [Calcul de la climatologie](https://github.com/Abdelmalek05/fire-detection-model/blob/0755f4e47f54a9e582b4f53d28f2a610098bbf1c/src/firerisk/ndvi.py) · [Données et incertitudes](SOURCES.md)
