# Réévaluation après la fusion de la PR 11

Le point de départ collectif est da93591. L’équipe rapporte 13,2/20 pour Atlas (ML 6,2/10, application 2,5/4, Git 2,2/3, documentation 2,3/3) et 17/20 pour Firewall. La grille indique le poids des critères. Seul le professeur peut expliquer les retraits individuels. [Grille officielle](https://github.com/hosniadilemp-a11y/DataMiningProjectPage/blob/e3a19efa610228e3d7615cc8182f6a097db820ab/mini_project_proposal.pdf) · [Fusion collective](https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/pull/11)

## Comparaison sur pièces

L’effort estimé porte sur le travail Atlas. P1 désigne la priorité scientifique ou la fiabilité de la classification, P2 la lisibilité et la recette.

| Sujet et critère | Projet Firewall | Wildfire Atlas au départ | Valeur, décision et effort | Preuves Firewall / Atlas |
|---|---|---|---|---|
| Expériences (1.1, 1.3) | Sept notebooks couvrent exploration, variantes, tuning, export et statistiques. | Trois notebooks communs, benchmark scripté, expériences K-NN/ACP avec schéma distinct. | Conserver les expériences séparées. L’intégration ACP demande à son auteur un manifeste à 24 entrées, une recherche sur train et un nouvel export compatible. P1, demi-journée de recette après livraison. | [notebooks][fn] · [contrat][wa] |
| Validation (1.4) | GridSearchCV, cinq plis stratifiés groupés par empreinte des onze attributs pour séparer les flux identiques. | Cinq années de validation successives, puis cinq plis mélangés sur train pour mesurer la sensibilité au mélange temporel. | Conserver les deux protocoles. Un mélange d’années expose le train au climat des années évaluées. L’ordre temporel répond à la question de transfert entre saisons. P1, vérification courte. | [tuning][ft] · [KFold][wk] |
| Statistiques (1.2) | Kruskal-Wallis sur les volumes, chi² sur variables catégorielles, tailles d’effet. | Tests des signes sur douze écarts annuels de cellules appariées, correction de Holm et sensibilité au mois. | Conserver la méthode liée au plan de collecte. Préciser l’unité d’inférence et le sens des effets. P2, une heure. | [tests scientifiques][fs] · [rapport][wr] |
| Classe rare (1.5) | Tableau par classe difficile avec vrais positifs, manqués et fausses alertes. | F1 de la classe positive pour les trois seuils du protocole. Coût en alertes difficile à lire pour le SVM retenu. | Implémenter les effectifs aux trois seuils sur 2024 et rendre le dénominateur visible. P1, deux heures. | [erreurs][fe] · [sélection][wt] |
| Probabilités et métriques (1.5) | Macro-F1, accuracy équilibrée et comparaison par classe. | Courbes ROC/PR, AP et Brier. Le score SVM dépend de la sélection des témoins. | Améliorer la lecture du score par tranche avec effectif et fréquence observée sur validation. Aucun recalibrage sur la saison de sélection. P1, une heure. | [métriques][fm] · [résultats][wr] |
| Parcours (2.1, 2.2) | Vues qualité, analyses, métriques et prédiction. | Six espaces, carte des cellules échantillonnées, météo, filtres persistants. | Conserver la carte et son périmètre incluant les cellules hors frontières. Enrichir Arena sur la cohorte 2024. P2, deux heures. | [application][fu] · [guide][wu] |
| Prédiction par lot (2.3) | Import CSV en plus de la saisie individuelle, validation avant prédiction. | Formulaire individuel et huit pipelines rechargeables. | Implémenter un lot numérique limité avec modèle choisi, seuil explicite, identifiant de ligne et export. P2, demi-journée. | [inférence][fi] · [studio][wp] |
| Validation des entrées (2.3) | Fonction de validation des attributs, plafonds de volume et de lignes. | Schéma, finitude et cohérence physique dans le formulaire. | Améliorer en partageant les contrôles avec le CSV, refuser colonnes interdites, champs dupliqués et lignes invalides avant inférence. P1, deux heures. | [contrôles][fi] · [services][wv] |
| Tests et CI (3.1) | Tests ciblés du lot, inférence et parcours, pytest dans Actions. | Tests du benchmark et de Streamlit, workflow Python. | Conserver la CI et ajouter des régressions qui comparent les classes du CSV et du formulaire. P1, deux heures. | [tests CSV][fb] · [workflow Atlas][wc] |
| Rapport et contributions (3.2, 4.1, 4.2) | Chapitres LaTeX et guide applicatif. Un seul auteur dans le shortlog de la copie examinée. | PDF reconstruit à partir des résultats, PR collectives, responsabilités distinctes et deux codes à confirmer. | Améliorer le rapport par les effectifs vérifiés et faire confirmer les codes. Rejeter toute réattribution et toute estimation de points par commit. P2, deux heures puis relecture équipe. | [chapitres][fd] · [fusions][wg] |

## Vérification des douze critères

| Critère (points) | État sur les pièces disponibles | Preuve actuelle | Limite et action | Contrôle et résultat attendu |
|---|---|---|---|---|
| 1.1 (2) | Conforme | config/protocole.json, src/preprocessing.py | Contrat secondaire à 25 variables, conserver le lot isolé. | test_final_benchmark et test_cleaning, 24 prédicteurs autorisés. |
| 1.2 (3) | Conforme | results/audit_siad03/statistiques_principal.csv | Dépendance entre années plausible, interpréter les tailles d’effet. | test_statistics, deux contrastes appariés sur train. |
| 1.3 (1) | Conforme | results/benchmark_final/manifest.json | Plafonds K-NN/SVM à signaler. | Rejouer les six inférences 2024 et comparer aux scores sauvegardés. |
| 1.4 (2) | Partiellement conforme | *_cv.csv et results/post_freeze/kfold_train | Accord pédagogique sur le choix principal en attente. | test_kfold_diagnostic, cinq plis, paramètres et scores concordants. |
| 1.5 (2) | Conforme | metrics.csv, decision.json, ROC/PR | Coût opérationnel inconnu. Détailler fausses alertes par seuil. | Retrouver le F1 gelé et compter toutes les lignes 2024. |
| 2.1 (1,5) | Conforme sur Linux | src/app.py, tests/test_ui_app.py | Recette sur poste universitaire à faire. | Ouvrir les six espaces, zéro exception. |
| 2.2 (1) | Conforme | src/eda_view.py, tests/test_eda.py | Les filtres modifient le dénominateur EDA. | Vérifier filtres vides, corrélations et retour de navigation. |
| 2.3 (1,5) | Conforme pour la saisie | src/ui/model_pages.py | Élargir aux lots pour réutiliser les pipelines sans ressaisie. | Score d’une ligne identique au formulaire, fichier invalide rejeté. |
| 3.1 (1) | Conforme localement | .github/workflows/tests.yml | Vérifier le run hébergé sur la tête de branche. | Suite locale verte puis contrôle de la CI sur GitHub. |
| 3.2 (2) | Partiellement conforme | Historique des fusions dont PR 11 | Contributions inégales, attribution individuelle par l’enseignant. | Relire les diffs et leurs auteurs, confirmer les périmètres en équipe. |
| 4.1 (1,5) | Conforme sur les pièces | docs/Rapport_MiniProject.md et PDF | Aligner le PDF avec les diagnostics. | Reconstruire, relire tableau et conclusions sur la bonne cohorte. |
| 4.2 (1,5) | Partiellement conforme | README, docs/SOURCES.md, docs/INTERFACE.md | Deux codes étudiants à confirmer. | Rejouer les commandes et obtenir les codes auprès des titulaires. |

[fn]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/tree/0ef2aa7272d67737f53688c62d8023e8e0aef165/notebooks
[ft]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/notebooks/05_full_tuning_benchmark.ipynb
[fs]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/src/statistical_tests.py
[fe]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/reports/minority_class_comparison.csv
[fm]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/src/models.py
[fu]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/src/app.py
[fi]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/src/inference.py
[fb]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/blob/0ef2aa7272d67737f53688c62d8023e8e0aef165/tests/test_batch_csv.py
[fd]: https://github.com/RSD-022/Firewall-Traffic-Analyzer/tree/0ef2aa7272d67737f53688c62d8023e8e0aef165/docs/latex/chapters
[wa]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/config/protocole.json
[wk]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/src/kfold_diagnostic.py
[wr]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/docs/Rapport_MiniProject.md
[wt]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/results/benchmark_final/thresholds_2024.csv
[wu]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/docs/INTERFACE.md
[wp]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/src/ui/model_pages.py
[wv]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/src/ui/services.py
[wc]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/da935911e99d798fa67aa007f69d28080f84caf2/.github/workflows/tests.yml
[wg]: https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/pull/11
