# Wildfire Atlas · dossier de réévaluation du 26 novembre 2026

**Version de départ.** Le dépôt collectif a été vérifié sur `da935911e99d798fa67aa007f69d28080f84caf2`, fusion de la PR 11. L’inventaire Git et la liste publique des PR indiquaient deux branches collectives, onze PR closes et zéro ouverte au début de la revue. Les refs du fork ont aussi été récupérées. Le code du professeur a été examiné aux versions e3a19ef (cahier) et cf39482 (exemple). La grille ci-dessous s’applique au parcours de classification supervisée. [Cahier officiel](https://github.com/hosniadilemp-a11y/DataMiningProjectPage/blob/e3a19efa610228e3d7615cc8182f6a097db820ab/mini_project_proposal.pdf) · [Exemple de référence](https://github.com/hosniadilemp-a11y/DataMiningProjectExample/tree/cf394821502d428478d4c07aa9e5785e1c98916b)

**Version évaluée.** Le code et le PDF testés correspondent au SHA `0df7278a9e6143d9ea156979e208b5552ecd9760`. Dans une archive distribuée par `git archive`, Git inscrit automatiquement le SHA final exact ici : `$Format:%H$`. Le dernier commit documentaire contient le présent bilan. Pour identifier la révision effectivement remise depuis le clone, exécuter `git rev-parse HEAD` et reporter son résultat dans la déclaration de rendu. La PR et la branche de révision portent le SHA de tête après publication.

## Avant et après intégration

| Version | Éléments vérifiés | Ce que change l’intégration |
|---|---|---|
| Collectif da93591 | 109 tests dans un clone et un venv propres. Six modèles obligatoires, deux supplémentaires, application six espaces, SVM gelé, PDF et CI déjà présents. | Le septième espace explique les scores. L’étude ajoute les distributions mensuelles et les conditions associées aux erreurs. |
| Branche SIAD03 7379a84 | Huit commits supplémentaires, comparaison des seuils, fiabilité, CSV strict, tests. | Son import borné est relié au travail IASD17 par une seule interface de prédiction. |
| Branche IASD17 56c9285 | Six commits originaux de 4bea315 à 56c9285. Suite d’origine rejouée, 169 tests réussis. Fichiers de prédiction, niveaux, SHAP, tests et documentation relus. | Le merge 5087612 a conservé les deux ascendances. Le conflit d’imports dans model_pages.py a été résolu sur la branche de révision. |
| Intégration finale | 234 tests réussis dans la copie de travail, puis 234 dans un clone indépendant avec conversion Windows des fins de ligne activée (`core.autocrlf=true`) sous Linux. Installation Python 3.12 indépendante, `pip check`, huit pipelines rechargés, sept pages parcourues. | La notice du studio, les preuves numériques et le PDF correspondent aux comportements testés. |

Le fichier brut (SHA-256 `cc260f954f76651c745c688c51e962a5fdbc4ee92d487ecd5577ba2aff7ecc26`), les 24 variables, le SVM publié (SHA-256 `969abdfb4f1d47197279d3e0e22e4dc6cef4e5007bb33499437c7eb32c94aa4b`), le protocole et les lots d’évaluation ont été contrôlés contre la base collective. La recette relit le résultat 2025 archivé. Le développement utilise le train et 2024.

## Conclusions de la revue IASD17

- **Explicabilité.** Le titre du beeswarm apparaissait sans points. Les arbres utilisaient une référence différente de celle annoncée. La permutation pouvait modifier une attribution entre deux appels identiques. Le graphe, la référence du train, l’ordre des attributs, le sens de la classe positive et la détermination des contributions sont maintenant contrôlés. En comparant le score natif à la base plus les contributions de 25 observations par modèle, le plus grand écart sur les huit pipelines atteint 6,78 × 10⁻⁸. L’égalité de la somme vérifie la décomposition du score. Pour six modèles, la répartition entre variables est estimée par quatre ordres de permutation. Le coût, l’effet des corrélations et les limites de l’échantillonnage sont documentés. [Revue, mesures de temps et mémoire](REVUE_SHAP.md)
- **Niveaux et import.** Deux parcours CSV concurrents validaient différemment les colonnes et les valeurs manquantes. Des colonnes extérieures pouvaient réapparaître dans l’export. Les tranches sont maintenant exprimées par intervalle de score. La classe dépend du seuil propre au modèle. Les tests confrontent l’import au formulaire, aux anciens exports et à des fichiers contenant valeurs invalides, formules ou champs de fuite. [Revue du studio](REVUE_STUDIO.md)
- **Attribution.** Les commits IASD17 et les deux notebooks de l’auteur du lot K-NN/ACP figurent dans l’historique avec leurs auteurs d’origine. La mise en cohérence, les diagnostics de développement et les contrôles de réévaluation relèvent du lot SIAD03. Le nom du projet et les codes déjà attestés suffisent aux supports publics.

## Relecture des douze critères

P1 désigne un point à traiter ou à défendre avant envoi, P2 une vérification de recette. La dernière colonne indique une preuve reproductible ou le contrôle humain encore nécessaire.

| Critère officiel et poids | Résultat actuel | Écart, action et priorité | Vérification |
|---|---|---|---|
| 1.1 Prétraitement, effectif et attributs · 2 | 121 869 × 37 au départ. Nettoyage reproduit. 24 variables numériques autorisées. Transformations ajustées dans le pli. | P2. Le schéma exploratoire à 25 entrées relève du lot secondaire. | tests/test_cleaning.py, tests/test_final_benchmark.py, config/protocole.json |
| 1.2 EDA et deux analyses justifiées · 3 | Signes des écarts annuels de température et humidité après appariement des cellules. Sept fichiers statistiques reproduits. | P2. Présenter les effets (+3,077 °C et −10,107 points) et la dépendance possible des années. | src/statistical_analysis.py, tests/test_statistics.py |
| 1.3 Classifieurs du cours · 1 | Six pipelines du benchmark et deux alternatives historiques. Scores 2024 et variables contrôlés. | P2. Annoncer les plafonds d’ajustement, 12 000 pour K-NN et 3 500 pour SVM. | manifest.json du benchmark, tests/test_final_benchmark.py |
| 1.4 Optimisation et K ≥ 5 · 2 | Grilles vérifiées à partir des fichiers de recherche. Cinq validations temporelles, cinq plis classiques complémentaires sur train. | P1. Faire confirmer le protocole principal et expliquer les années présentes de chaque côté du KFold mélangé. | src/kfold_diagnostic.py, tests/test_kfold_diagnostic.py |
| 1.5 Métriques, matrices et courbes · 2 | Scores par modèle, confusions, ROC, AP, F1, erreurs mensuelles, géographiques et météo. | P2. Les coûts de mobilisation sont inconnus. Les scores individuels hors pli de 2019–2023 manquent pour reconstruire leurs FP/FN annuels. | tests/test_validation_alerts.py, tests/test_development_profiles.py |
| 2.1 Application locale et stabilité · 1,5 | Installation indépendante, interactions dans Chromium, cache SHAP, conservation de la cohorte au retour vers Arena. | P1. Recette sur le matériel réel de soutenance. | tests/test_navigation_final.py, RECETTE_INTERFACE.md |
| 2.2 Six composants EDA · 1 | Statistiques, manquants, histogramme/KDE, fréquences, corrélations et filtres présents. | P2. Indiquer le dénominateur après sélection et le sous-échantillonnage de la densité. | src/eda_view.py et tests/test_eda.py |
| 2.3 Classe et score interactifs · 1,5 | Saisie individuelle, lots CSV, tranches descriptives et waterfall du pipeline soumis. | P2. Discuter la fiabilité et le petit nombre de références utilisé pour les explications. | REVUE_STUDIO.md, REVUE_SHAP.md, tests/test_ui_app.py |
| 3.1 Structure et dépendances · 1 | Répertoires, versions fixées, données locales et CI Python 3.12. | P2. Vérifier le résultat de CI sur le SHA de remise. | .github/workflows/tests.yml, requirements-dev.txt |
| 3.2 Contributions régulières · 2 | Branches SIAD03 et IASD17 intégrées avec leur ascendance. Les commits documentent les lots réellement livrés. | P1. La répartition temporelle des contributions est inégale. L’enseignant apprécie le travail individuel. | git log --graph et matrice du README |
| 4.1 Rapport PDF scientifique · 1,5 | Rapport régénéré avec résultats, figures, capture réelle et explications. | P2. Relire le PDF depuis le commit destiné au professeur. | python -m src.build_report --verify et contrôle des pages rendues |
| 4.2 README et matrice des rôles · 1,5 | Sources, lancement Windows/Linux, dépendances, captures, reproduction et rôles reliés aux livraisons. | P1. Faire confirmer par son titulaire le code de l’auteur de 39531eb. | README.md, docs/SOURCES.md, vérification des liens |

## Résultats et portée

Le train contient 27,2 % de cellules-jours positives, contre 7,6 % en validation. Sur les 2 299 observations de 2024 au-dessus de 34,2 °C, le SVM retrouve 244 des 248 détections et produit 2 015 fausses alertes. À 0,20 sur toute la validation, il retrouve 475 des 643 détections. Jusqu’à 0,35, les F1 sont proches mais la différence atteint 2 216 fausses alertes. Ces nombres décrivent les lignes échantillonnées. La météo contemporaine, le choix des témoins et le changement de saison limitent toute interprétation prospective. [Profils par mois, bloc géographique et météo](DIAGNOSTIC_DEVELOPPEMENT.md)

La validation chronologique évalue le transfert à une année postérieure, alors que le KFold classique mélange les saisons et permet des cellules voisines dans les deux ensembles. Les contrôles ont vérifié les effectifs, les scores par pli, les paramètres des objets et la correspondance avec les scores enregistrés. Le test final publié donne 900 vrais positifs, 222 faux négatifs et 4 814 faux positifs. Il sert à décrire la seule règle gelée avant 2025. [Vérification scientifique et notebooks](VERIFICATION_SCIENTIFIQUE.md)

## Appréciation indicative

La seule note communiquée est **13,2/20**. Notre estimation de préparation du dossier collectif se situe **entre 16 et 18/20**. Les éléments les plus solides pour la réévaluation sont les deux validations vérifiables, les courbes et erreurs interprétées, et la prédiction testée de bout en bout. Le haut de la fourchette suppose que l’enseignant accepte la justification temporelle, juge les contributions personnelles suffisantes et retrouve le même fonctionnement sur son poste. La note individuelle et les points retirés à chaque sous-critère restent inconnus.

## Checklist de remise

- [x] Relire les deux branches et vérifier que les six commits IASD17 restent ancêtres de la version intégrée.
- [x] Contrôler les empreintes, les six modèles obligatoires, les deux supplémentaires et les prédictions de validation.
- [x] Exécuter les notebooks et la suite locale, rejouer les statistiques et vérifier les tableaux du PDF.
- [x] Parcourir l’application et tester l’export, sa réimportation et le refus d’entrées invalides.
- [ ] Confirmer le troisième code étudiant et relire collectivement les rôles et l’anonymat des supports.
- [ ] Tester la présentation sur le poste de soutenance et consulter la CI pour le commit proposé.
- [ ] Faire relire la PR, choisir le commit de remise, puis transmettre son SHA, le PDF et les changements au professeur selon la procédure de l’équipe. [Brouillon de notification](reevaluation/NOTE_EQUIPE_PEDAGOGIQUE.md)

Le rapport de 13 pages comporte neuf illustrations. La vérification automatique relit onze tableaux, soit 49 lignes. [Texte proposé pour la PR](PR_REEVALUATION.md)

Le détail des fichiers modifiés est disponible par `git diff --name-status da935911e99d798fa67aa007f69d28080f84caf2 HEAD`. Les modules principaux de ce lot sont `src/development_profiles.py`, `src/explainability/`, `src/ui/` et `src/build_report.py`. Les sorties de l’analyse sont regroupées dans `results/post_freeze/development_profiles/`.
