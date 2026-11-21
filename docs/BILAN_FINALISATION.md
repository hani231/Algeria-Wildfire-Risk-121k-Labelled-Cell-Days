# Bilan de finalisation

Base collective auditée : `ed8939f`, 21 novembre 2026. L’unité d’analyse est une cellule géographique observée un jour donné. Les mesures météo de la journée servent à classer rétrospectivement la présence d’une détection satellitaire dans un échantillon de jours. La prévalence de cet échantillon dépend du choix des jours négatifs.

| Critère (maximum) | Avant | Après et preuve | Estimation indicative |
|---|---|---|---:|
| Prétraitement (2) | 24 entrées numériques, exclusions et contrôles implémentés | Notebook 02 et contrôle de provenance exécutés, histoire FIRMS complète indisponible | 1,9 |
| Exploration et statistiques (3) | Deux études appariées et sensibilité mensuelle | PDF avec écarts annuels, distributions et corrélations. Indépendance entre saisons incertaine | 2,7 |
| Classifieurs (1) | Six modèles attendus présents | Artefacts relus par les tests, deux extensions distinguées | 1 |
| Optimisation (2) | Cinq plis temporels, certaines grilles réduites | Variantes isolées dans results/post_freeze/parameters, sensibilité à la taille, acceptation du choix temporel à confirmer | 1,6 |
| Comparaison (2) | Métriques, confusion, coûts, ROC/PR | PDF avec scores des cinq plis et dispersion, matrice 2025 et repère toujours positif | 1,8 |
| Application (1,5) | Six espaces Streamlit | Navigation testée, procédure de recette Windows et petit écran dans INTERFACE.md | 1,3 |
| EDA interactive (1) | Six fonctions accessibles | Tests de navigation et filtres. Les proportions sont propres à l’échantillon | 0,9 |
| Prédiction (1,5) | Huit pipelines, seuil appliqué lors du calcul | Seuil visible avant soumission, test dédié pour le SVM | 1,4 |
| Structure (1) | Deux notebooks historiques, brut dans Dataset | Deux points d’entrée ajoutés et pointeur dans data/raw. Cellules des quatre notebooks exécutées dans une copie | 0,9 |
| Contributions (2) | Historique des travaux réels | Attribution historique conservée. Deux codes à compléter par leurs titulaires | À évaluer individuellement |
| Rapport (1,5) | PDF de sept pages, tableau comparatif serré | PDF régénéré, tableaux lisibles, figures et résultats post-gel séparés | 1,4 |
| README (1,5) | Installation après clonage et commandes du lot publié | Clone, reproduction, notebooks, moteur PDF et expériences complémentaires documentés | 1,4 |

Sous-total technique indicatif : 16,3/18. Les contributions peuvent ajouter jusqu’à 2 points. Ce chiffrage est une appréciation pédagogique. La reproduction des scores dans cet échantillon ne valide pas un usage opérationnel.

## Lecture à défendre à l’oral

Sur 8 467 observations de 2025, le SVM gelé au seuil 0,20 retrouve 900 des 1 122 détections. Parmi ses 5 714 alertes, 4 814 correspondent à des lignes étiquetées sans détection. La régression logistique avait obtenu un meilleur F1 sur 2024 au seuil standard mais ne figurait pas dans les six candidats à la décision finale. La comparaison 2025 reste celle de la règle enregistrée avant publication des résultats.

L’expérience de taille utilise uniquement 2024 pour la mesure. Au seuil 0,50, doubler l’effectif de K-NN de 6 000 à 12 000 lignes laisse le F1 moyen proche de 0,128. La variabilité entre trois tirages sur une seule saison ne mesure pas l’incertitude sur une saison future.

## Portée des vérifications

La reproduction du test gelé donne des fichiers result.json et predictions.csv identiques aux fichiers publiés. Le contrôle producteur retrouve 3 348 clés cellule/date et 7 481 divergences sur 98 822 antécédents visibles. Les quatre notebooks ont été vérifiés par exécution séquentielle de leurs cellules dans IPython sur une copie du dépôt. La connexion à un noyau Jupyter externe n’a pas été testée avec succès dans cet environnement. La recette visuelle sur le poste de soutenance, les codes étudiants des deux autres membres et la décision du professeur sur les plis chronologiques restent à confirmer.

Le fichier nettoyé reconstruit par le notebook 01 est identique octet par octet à data/processed/dataset_clean.csv. Le contrôle automatique du studio parcourt les six espaces et lance une prédiction avec chacun des huit pipelines. Une recette graphique sur un appareil réel reste utile pour vérifier les dimensions et le confort des interactions.
