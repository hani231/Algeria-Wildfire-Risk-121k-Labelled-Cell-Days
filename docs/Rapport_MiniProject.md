---
title: "Wildfire Atlas"
subtitle: "Classification rétrospective des détections en Algérie et dans les cellules voisines"
author: "Mini-projet de fouille de données · Contribution d’intégration SIAD03"
date: "21 novembre 2026"
geometry: "a4paper,margin=21mm"
fontsize: 11pt
colorlinks: true
---

# Question de recherche

Peut-on distinguer les cellules-jours avec détection satellitaire à partir de la météo, de la végétation et de la saison ? La cible vaut 1 lorsqu’une détection répond aux critères du producteur. Les négatifs sont échantillonnés. La proportion de jours positifs dans le tableau dépend de ce plan de collecte.

Notre comparaison porte sur six familles de classifieurs et cinq plis chronologiques. Un seuil choisi sur 2024 est ensuite évalué sur une saison tenue à l’écart. Sur 8 467 cellules-jours de 2025, la règle gelée retrouve 900 détections et produit 4 814 faux positifs. La précision de 15,8 % limite son intérêt comme alerte. La météo de la journée limite également son usage prospectif.

# Données et unités

Le fichier compte 121 869 lignes, 37 colonnes et 1 423 cellules de 0,1°. Il couvre juin à octobre de 2012 à 2025. Le rectangle d’étude inclut des cellules marocaines, tunisiennes et espagnoles. Nous conservons la population d’origine. Le producteur assemble détections VIIRS, météo ERA5-Land via Open-Meteo et indices MODIS/Terra MOD13Q1 v061.

| Famille | Mesures et unités |
|---|---|
| Météo du jour | Température min./moy./max. (°C), humidité min./moy. (%), vent moyen/max. (km/h), pluie (mm), déficit de pression de vapeur (kPa). |
| Historique météo | Pluie sur 7/30 jours (mm), jours depuis une pluie de 1 mm, moyennes sur 7 jours de température et d’humidité. |
| Indices de feu | FFMC, DMC, DC, ISI, BUI, FWI. Les agrégats journaliers et la réinitialisation annuelle limitent l’interprétation des seuils usuels. |
| Végétation et saison | NDVI, variation sur environ 32 jours, âge du composite (jours), jour dans l’année. |

Le dictionnaire complet et les conditions de licence figurent dans *docs/dictionnaire_colonnes.md* et *docs/SOURCES.md*.

\newpage

# Nettoyage et exploration

L’audit vérifie les dates, la clé cellule/jour, les bornes physiques et les doublons. Aucun doublon exact ni violation des contrôles physiques répertoriés dans le fichier audité. Les trois variables *sample_kind*, *n_detections* et *max_frp* dérivent de la sélection ou de la cible. Elles sont retirées avant modélisation. La cible, la partition, les coordonnées, l’identifiant et l’année restent hors de la matrice explicative.

Le code source du producteur impose un délai pour l’historique des feux, un composite NDVI déjà clos et une normale 2000–2011. Les dates de construction et les événements FIRMS complets sont absents du CSV. La comparaison vérifiée sur 3 348 lignes communes à l’échantillon public soutient l’identification de la version, mais une reconstruction du combustible à partir du seul train laisse 7 481 écarts sur 98 822 antécédents visibles. Nous conservons l’exclusion de *days_since_last_fire*, *ndvi_normal* et *ndvi_anomaly*.

![Effectifs et part observée par année d’entraînement. Les variations concernent les cellules-jours échantillonnées.](results/siad03_extensions/exploration/annual.png){width=82%}

Le train contient 28 586 positifs sur 104 979 lignes (27,2 %). En 2024 il y en a 643 sur 8 423 (7,6 %). Un modèle trouvant bien la classe dominante peut donc manquer la totalité des détections. L’application permet de contrôler les valeurs manquantes, les distributions, les fréquences et les corrélations après chaque filtre. Une KDE représente la distribution d’une mesure de l’échantillon.

\newpage

# Associations de température et d’humidité

Pour chacune des deux variables, on compare les moyennes des classes dans chaque couple cellule/année où les deux classes existent. On calcule ensuite les écarts moyens annuels. Cette agrégation réduit la pseudo-réplication des cellules-jours. Le test binomial exact des signes porte sur les années aux écarts non nuls. Sous H0, un écart positif a une probabilité de 0,5. H1 est bilatérale. Le choix du test évite une hypothèse de normalité sur douze amplitudes annuelles.

| Appariement | Écart moyen de température maximale | Écart moyen d’humidité |
|---|---:|---:|
| Cellule et année | +3,077 °C | −10,107 points |
| Cellule, année et mois | +2,307 °C | −9,591 points |

Dans les deux analyses, les douze années vont dans le sens d’une température plus élevée et d’une humidité plus basse les jours positifs. Pour chaque variable, p brute = 0,00048828. Holm corrige les deux tests de chaque famille, avec p ajustée = 0,00097656. La sensibilité mensuelle réduit l’amplitude des différences. Elle réutilise les mêmes observations. L’indépendance des saisons demeure incertaine et les associations ne permettent aucune conclusion causale.

# Évaluation chronologique

Le train couvre 2012–2023. Chaque pli interne valide une année entière de 2019 à 2023 et n’apprend que sur les années antérieures. Cette adaptation du K-Fold demandé empêche l’apprentissage sur des années futures. Son acceptation pédagogique reste à confirmer. Le choix interne maximise le F1 moyen de la classe 1 à seuil 0,50. Imputation médiane, standardisation et pondérations sont apprises sur le sous-ensemble d’apprentissage de chaque pli.

La validation 2024 compare ensuite les six modèles et les seuils 0,20, 0,35 et 0,50 par F1. À égalité, priorité au seuil le plus élevé puis à l’ordre alphabétique. La règle et les candidats étaient fixés avant cette comparaison. L’examen historique répété de 2024 limite l’indépendance de toute estimation sur cette saison. L’artefact gagnant et son seuil ont été gelés dans Git avant l’ouverture de 2025. Aucun réajustement sur 2012–2024.

\newpage

# Six familles et coût de recherche

**Zero-R** apprend la classe majoritaire et constitue le point de comparaison sans hyperparamètre. **GaussianNB** combine des distributions conditionnelles gaussiennes. Les corrélations météo fragilisent son hypothèse d’indépendance. Le lissage de variance explore 14 valeurs de $10^{-12}$ à 10. La sélection retient 1. Le lot historique à sept candidats obtenait un F1 2024 de 0,176681 contre 0,173585 dans la grille étendue.

**K-NN** vote à partir des distances entre observations standardisées. Les configurations comparent 15/45 voisins, les distances Manhattan/euclidienne et les poids uniformes/inverses. Le réglage retenu est 15 voisins euclidiens à poids uniformes. **SVM** ajuste une séparation de marge maximale et convertit les marges en scores probabilistes par calibration interne aux données d’apprentissage. Les six configurations explorent linéaire, RBF et polynomial de degré 2 avec régularisation et gamma. Le gagnant interne est linéaire, C = 0,1.

**L’arbre** sépare les observations par seuils. Quatre configurations combinent Gini/entropie avec profondeur, taille des feuilles et élagage. Le nouvel arbre retient Gini, profondeur 10, minimum 80 par feuille et alpha 0,0002. Il remplace l’artefact historique scikit-learn 1.9.1 dans l’interface. **La forêt** moyenne plusieurs arbres bootstrap et échantillonne les variables aux divisions. Trois configurations comparent nombre d’arbres, profondeur, feuilles, fraction de variables et pondération. La sélection retient 32 arbres, profondeur 10, minimum 50 par feuille, fraction 0,4 et classes équilibrées.

Les grilles sont limitées pour maîtriser le coût. Chaque pli d’apprentissage et ajustement final de K-NN est plafonné à 12 000 lignes, celui de SVM à 3 500, tirées de façon stratifiée avec graine 42. Les autres modèles utilisent tout le train autorisé. Les cohortes de validation restent entières. Les résultats ne caractérisent pas un SVM ou un K-NN ajusté sur 104 979 lignes.

{{COUTS}}

Recherche = temps mural pour la grille complète. Ajustement = entraînement final seul. Scores = prédiction des 8 423 lignes. Les temps dépendent de la machine.

\newpage

# Comparaison sur 2024

Chaque ligne utilise la même cohorte et le seuil 0,50. L’accuracy équilibrée moyenne sensibilité et spécificité. L’Average Precision (AP) pondère la précision par les gains de rappel, selon la définition non interpolée de scikit-learn.

{{SCORES}}

{{CONFUSIONS}}

![Discrimination sur les scores de validation. Les pointillés indiquent la diagonale ROC et la prévalence pour la précision-rappel.](results/benchmark_final/courbes_2024.png){width=94%}

Les deux modèles supplémentaires, régression logistique et HistGradientBoosting, conservent leurs lots de 2024 (F1 respectifs 0,1847 et 0,1673 à 0,50). La sélection finale était limitée aux six modèles requis. Zero-R dépasse 92 % d’accuracy en prédisant toujours zéro et manque les 643 positifs. L’arbre et la forêt pondérés améliorent le rappel, avec davantage de fausses alertes.

\newpage

# Sensibilités et limites

À lissage GaussianNB fixé à 1, nous avons réduit les variables sur les cinq mêmes plis, en conservant imputation, échelle et seuil. Le tableau donne la moyenne des scores annuels.

{{ABLATION}}

L’ajout d’historique, d’indices et de végétation améliore peu le F1 moyen par rapport à la météo seule. L’AP moyenne est même supérieure avec les seules mesures du jour. Les variables supplémentaires peuvent être redondantes pour GaussianNB. Cette ablation décrit ce modèle.

Au seuil 0,50, le F1 de GaussianNB tombe de 0,410 en CV à 0,174 en 2024. La fréquence plus faible des détections en 2024 diminue la précision à taux d’erreurs comparables. Le changement de population est une explication plausible et non une décomposition causale de la baisse. Les strates spatiales comprennent des blocs sans positif, où le rappel et la ROC-AUC sont indéfinis.

Pour le SVM au seuil 0,20, le rappel 2024 varie de 0,585 en septembre à 0,941 en août. Le score de Brier vaut 0,110 sur la saison. Les probabilités dépendent de l’échantillonnage et de la calibration interne. Dans l’analyse historique de la régression logistique, permuter FWI ou température moyenne *à l’intérieur des mois* abaisse l’AP d’environ 0,041 et 0,040. Ces perturbations de variables corrélées ne prouvent pas un effet causal. Le bootstrap historique de cellules (300 réplications) donne un intervalle de F1 [0,1655 ; 0,2041] pour la régression logistique sur 2024. Il ne mesure pas l’incertitude d’une saison future.

# Résultat final sur 2025

Le SVM au seuil 0,20 obtient un F1 de 0,176646 sur la validation utilisée pour le sélectionner. Au seuil 0,35, il obtenait 0,175832. Les choix très proches renforcent l’intérêt du test réservé. Le modèle de 3 500 observations a été conservé à l’identique, avec vérification des empreintes SHA-256 de l’artefact, de la configuration et du CSV avant l’évaluation.

{{TEST}}

Sur 8 467 lignes, le résultat final comprend **900 vrais positifs, 222 faux négatifs, 4 814 faux positifs et 2 531 vrais négatifs**. La hausse du F1 intervient dans un échantillon comptant davantage de positifs (13,3 %). La ROC-AUC reste modeste. Cette expérience soutient une classification rétrospective exploratoire. Une alerte opérationnelle demanderait des mesures connues à l’avance, une évaluation prospective et une estimation des coûts des erreurs.

\newpage

# Application, contributions et reproduction

![Wildfire Atlas. La carte regroupe les cellules-jours observées par cellule.](docs/interface-bureau.png){width=78%}

Command Center synthétise la couverture. Data Explorer partage les filtres entre statistiques descriptives, données manquantes, histogramme/KDE, fréquences, corrélations et export. Geo Intelligence contrôle les coordonnées. Model Arena rattache scores, courbes et matrices à leurs fichiers d’expérience. Prediction Studio valide le schéma et les mesures avant de charger le pipeline sauvegardé. Scientific Insights présente le protocole et les tests appariés.

Le dépôt collectif apporte les observations, le cadrage et un arbre historique. Le lot SIAD03 comprend audit, nettoyage, statistiques, EDA, Zero-R/NB et interface. La branche d’intégration SIAD03 ajoute les recherches K-NN, SVM, forêt et arbre compatible, le gel du modèle et ce rapport, avec assistance de développement. Le plan initial décrit une répartition prévue. L’historique Git établit les livraisons effectives.

Depuis la racine, installer *requirements-dev.txt* sous Python 3.12. Lancer *python -m pytest -q* puis *python -m streamlit run src/app.py*. La commande *python -m src.models --output results/local_runs/benchmark* répète le développement dans un dossier neuf. Le README décrit la reproduction séparée du test gelé et de ce PDF. Les prédictions, paramètres par pli, versions et empreintes sont disponibles dans *results/benchmark_final/*.

**Références.** [Cahier du mini-projet](https://github.com/hosniadilemp-a11y/DataMiningProjectPage) · [Dictionnaire du producteur](https://github.com/Abdelmalek05/fire-detection-model/blob/0755f4e47f54a9e582b4f53d28f2a610098bbf1c/docs/DATASET.md) · [Jeu de données](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days) · [Validation croisée scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html) · [Test binomial exact SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html). Données sous CC BY 4.0, attributions complètes dans *docs/SOURCES.md*.
