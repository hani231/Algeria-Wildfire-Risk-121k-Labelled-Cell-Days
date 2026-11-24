# Réévaluation de Wildfire Atlas

Base collective du 24 novembre 2026, commit `39531eb`. La note communiquée par l’équipe est 13,2/20, répartie en 6,2/10, 2,5/4, 2,2/3 et 2,3/3. L’identité du commit initialement noté et la ventilation des retraits par ligne restent inconnues. Le tableau évalue les preuves disponibles au début de cette intervention. [Grille officielle, source e3a19ef](https://github.com/hosniadilemp-a11y/DataMiningProjectPage/blob/e3a19efa610228e3d7615cc8182f6a097db820ab/mini_project_proposal.pdf)

| Critère et exigence officielle | Existant et preuve | État initial | Écart, action prévue et potentiel |
|---|---|---|---|
| 1.1 · 2 · ≥10 000 lignes et ≥10 attributs, valeurs manquantes/aberrantes, encodage et échelles justifiés | 121 869 × 37. clean_data et coherence_counts contrôlent bornes et clés. Imputation et échelle apprises dans le pipeline. Identifiants et catégories hors X, 9999 est une sentinelle d’historique exclu. tests/test_cleaning.py | Conforme pour le lot gelé | P1. Expliquer pourquoi les 25 variables des notebooks secondaires ne peuvent entrer dans ce contrat. Potentiel de clarification. |
| 1.2 · 3 · Distributions, corrélations, au moins deux analyses justifiées | src/statistical_analysis.py, tests/test_statistics.py, CSV principal et sensibilité. Tests des signes appariés température et humidité, correction de Holm | Conforme | P2. Reproduire les sorties. L’indépendance entre années reste une hypothèse. Potentiel limité. |
| 1.3 · 1 · Six classifieurs supervisés obligatoires | src/models.py, six fichiers joblib et manifest.json dans results/benchmark_final. Deux modèles supplémentaires identifiés | Conforme au benchmark | P1. Documenter la provenance des quatre nouveaux objets ACP avant toute intégration. Potentiel de traçabilité. |
| 1.4 · 2 · GridSearchCV/RandomizedSearchCV et K-Fold ≥5 pour tout modèle réglable | GridSearchCV emploie cinq validations annuelles 2019–2023. Grilles, meilleurs paramètres, effectifs et scores de pli sauvegardés. Zero-R exempté | Partiel | P1. Vérifier la concordance estimateurs/CSV. Mesurer un KFold classique complémentaire sur le train de SIAD03. L’accord du professeur sur le protocole principal reste ouvert. Potentiel élevé. |
| 1.5 · 2 · Tableau multicritère, matrices, ROC, précision/rappel/F1 | src/siad03_extensions/evaluation.py et tests/test_final_benchmark.py. AP, temps, budget des ajustements, seuils 0,50/0,20 et test gelé documentés | Conforme au benchmark | P1. Distinguer AP des notebooks et expérience comparable. Surapprentissage et sous-apprentissage exigent des scores apprentissage/validation associés. Potentiel moyen. |
| 2.1 · 1,5 · Exécution locale, stabilité et architecture | src/app.py et src/ui/, cache et gestion des artefacts. Huit pipelines compatibles. | Conforme sur Linux | P2. Recette dans un nouveau venv et sur trois largeurs. Poste universitaire non vérifié. Potentiel modéré. |
| 2.2 · 1 · Six composants EDA | src/eda_view.py, tests/test_eda.py. Statistiques, manquants, distributions/KDE, fréquences, heatmap, filtres partagés | Conforme | P2. Vérifier les interactions et cas limites. Éviter une refonte générale. Potentiel limité. |
| 2.3 · 1,5 · Formulaire de classification immédiate avec confiance | src/ui/model_pages.py, tests/test_ui_app.py. Mesures et seuil contrôlés. Le résultat dépend du clic de soumission et disparaît au rerun, contrairement aux filtres EDA persistés | Partiel | P1. Conserver dernier calcul et mesures soumises dans la session, indiquer le modèle associé et tester le retour de navigation. Potentiel élevé côté UI. |
| 3.1 · 1 · Structure data/notebooks/src/docs, requirements et commits clairs | data/raw/README.md pointe vers le brut unique, requirements-dev.txt et .github/workflows/tests.yml existent | Conforme pour la structure | P2. Vérifier installation, CI si accessible et chemins des nouvelles preuves. Potentiel limité. |
| 3.2 · 2 · Historique individuel régulier et authentique | git shortlog --no-merges et git log --first-parent sur 39531eb. SIAD03 a 58 commits non-merge sur sept dates et dix fusions de branches de son fork. Les deux autres historiques comptent 32 et 1 commits | Partiel pour l’équipe | P2. Relier lots et auteurs réels. La pondération appartient au professeur. Un historique individuel peu fourni ne se corrige pas en réattribuant le travail. Gain non chiffrable. |
| 4.1 · 1,5 · PDF académique avec théorie, méthode, résultats et interprétation | docs/Rapport_MiniProject.pdf, gabarit Markdown, src/build_report.py. Annexe K-NN/ACP ajoutée après le PDF | Partiel | P1. Réconcilier le PDF collectif avec l’annexe et les résultats complémentaires. Potentiel modéré. |
| 4.2 · 1,5 · README, installation, accès aux données, rôles par codes et synthèse justifiée | README, docs/SOURCES.md, docs/INTERFACE.md | Partiel | P2. Ajouter les commandes et la distinction entre lots. Deux codes restent à confirmer par leurs titulaires. Potentiel limité. |

## Responsabilités et décision sur l’expérience secondaire

La fusion #9 a intégré le benchmark gelé. La fusion #10 a ajouté les analyses de sensibilité et les diagnostics. Le commit suivant appartient au responsable des notebooks K-NN et ACP. Dans les deux notebooks, la liste écrite à la main ajoute ndvi_normal et place doy en tête. Le code du producteur calcule une normale sur 2000–2011. Sa présence dans la liste secondaire est constatée ; sa justification par l’auteur et la provenance complète du CSV restent à confirmer. L’inclusion ne démontre pas à elle seule une fuite. Les colonnes de fuite directe sont absentes des deux listes.

Imputation, échelle et ACP sont ajustées sur le train. Le code transforme aussi 2025, sans score de test trouvé dans ces notebooks. Les nombreux choix de K et rétentions sont examinés sur la même validation 2024. L’ACP 97 % y est transformée mais sa performance demeure en attente. Le PDF secondaire nomme « PR-AUC » la fonction average_precision_score. En 1.8.0, le chargement individuel des quatre artefacts signale explicitement une sérialisation en 1.9.0.

**Proposition destinée au responsable** : déclarer le schéma ordonné et la version dans un manifeste propre, réunir imputation, standardisation, ACP et K-NN en Pipeline et déplacer la recherche de K et de rétention dans les plis du train. Exclure 2025 du workflow exploratoire. Avant toute intégration, comparer avec/sans normale à budget et cohortes identiques. Cette proposition ne modifie aucun fichier de l’auteur.

## Décision de travail

Traiter d’abord les preuves ML et le cas K-Fold sur GaussianNB, puis la persistance du studio et sa recette. Régénérer le PDF et compléter le bilan à partir des vérifications effectivement exécutées. La décision SVM du commit ece0598 et son évaluation 2025 restent les références.

## Bilan après exécution

Le diagnostic a finalement pu couvrir les six grilles dans le budget de calcul. Le lot sous results/post_freeze/kfold_train est indépendant des artefacts officiels. KFold utilise les 104 979 lignes de 2012–2023, cinq plis mélangés, graine 42 et les mêmes plafonds d’apprentissage que le benchmark. Aucune recherche de seuil et aucun refit. Les tests vérifient le meilleur réglage publié de chaque recherche chronologique, ses scores par pli et les paramètres de l’estimateur rechargé.

| Critère | Avant → après | Preuve supplémentaire et limite |
|---|---|---|
| 1.1 | Conforme → conforme, périmètre précisé | 24 entrées officielles comparées aux 25 des deux notebooks. Le schéma expérimental ne rejoint pas le studio. |
| 1.2 | Conforme → conforme, reproduction vérifiée | Commande src.statistical_analysis exécutée dans un dossier temporaire. Les sept sorties des deux appariements ont été comparées octet par octet. Effets principaux +3,077 °C et −10,107 points, p ajustée 0,0009765625. |
| 1.3 | Conforme → conforme, lot secondaire identifié | Les deux notebooks ont été rejoués dans une copie isolée avec scikit-learn 1.9.0. Relecture indépendante des quatre objets publiés : AP 0,105224847886 sur 8 423 observations de validation. |
| 1.4 | Partiel → KFold classique exécuté en complément | src/kfold_diagnostic.py, tests/test_kfold_diagnostic.py et six CSV complets. L’acceptation de la sélection officielle chronologique dépend du professeur. |
| 1.5 | Conforme → conforme, comparabilité explicitée | Pour GaussianNB, F1 moyen de validation 0,507 en KFold et 0,410 en chronologique au même réglage. Pour le SVM, 0,301 et 0,412. Les populations évaluées diffèrent. Tableau complet en page 5 du rapport. |
| 2.1 | Conforme Linux → vérifié dans un venv neuf | Installation depuis requirements-dev.txt, navigation des six espaces et classification en Chromium. Recette sur le poste universitaire ouverte. |
| 2.2 | Conforme → conforme, cas limite corrigé | Deux points communs pouvaient donner une corrélation parfaite. Les effectifs communs, constantes et paires indisponibles sont désormais traités explicitement. tests/test_eda.py. |
| 2.3 | Partiel → conforme aux parcours testés | tests/test_ui_app.py vérifie le brouillon conservé, la dernière soumission et l’invalidation après modification. Le panneau final de Model Arena lit seulement le JSON publié. |
| 3.1 | Conforme → conforme localement | Suite initiale 98 tests, suite finale 109 tests ; installation isolée Python 3.12. L’état de GitHub Actions est non vérifié, API bloquée. |
| 3.2 | Partiel équipe → traçabilité du lot renforcée | Commits par sujet. La contribution K-NN/ACP demeure attribuée à son auteur. La réévaluation individuelle dépend des éléments du professeur. |
| 4.1 | Partiel → PDF régénéré et contrôlé | Rapport de 11 pages, tableaux KFold générés depuis les CSV, interprétation ACP et contrôle des pages rendues. Relecture de l’équipe avant transmission. |
| 4.2 | Partiel → reproduction documentée | Commande KFold, coexistence des environnements et guide illustré à trois largeurs. Les codes non confirmés restent à vérifier avec leurs titulaires. |

### Reproduire le contrôle secondaire

Dans une copie de travail temporaire, créer un venv Python 3.12 distinct et y installer scikit-learn==1.9.0, pandas==2.2.3, matplotlib, nbclient, nbformat et ipykernel. Lancer un noyau de cet environnement depuis notebooks/, puis exécuter 04_knn.ipynb et acp.ipynb. Le second écrit quatre fichiers sous models/, d’où l’intérêt de la copie temporaire. Pour vérifier les objets déjà publiés indépendamment du notebook, charger imputer, scaler, pca_95 et knn_pca_95 dans cet ordre. Retenir les lignes val du CSV nettoyé, ordonner les colonnes selon imputer.feature_names_in_, appliquer les trois transform puis predict_proba et average_precision_score. Les modèles secondaires n’ont été ni adoptés ni optimisés sur 2025.

### Portée pour la notation

La marge arithmétique jusqu’à 18 est de 4,8 points. ML et UI réunissent 5,3 points précédemment non attribués, mais les catégories ne détaillent pas la cause de chaque perte. Les preuves les plus substantielles concernent 1.4, 1.5 et 2.3. Les vérifications supplémentaires consolident surtout les autres lignes. Sans retour détaillé du professeur, convertir ces changements en gain numérique serait spéculatif.
