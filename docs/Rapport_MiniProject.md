---
title: "Wildfire Atlas"
subtitle: "Classification rétrospective des détections en Algérie et dans les cellules voisines"
author: "Mini-projet collectif de fouille de données"
date: "26 novembre 2026"
geometry: "a4paper,margin=21mm"
fontsize: 11pt
colorlinks: true
---

# Résumé et question de recherche

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

Le train contient 28 586 positifs sur 104 979 lignes (27,2 %). En 2024 il y en a 643 sur 8 423 (7,6 %). Un modèle trouvant bien la classe dominante peut donc manquer la totalité des détections. L’application permet de contrôler les valeurs manquantes, les distributions, les fréquences et les corrélations après chaque filtre. Les 24 entrées du modèle sont déjà numériques. Aucun encodage de catégories n’est nécessaire. Une KDE représente la distribution d’une mesure de l’échantillon.

\newpage

# Associations de température et d’humidité

Pour chacune des deux variables, on compare les moyennes des classes dans chaque couple cellule/année où les deux classes existent. On calcule ensuite les écarts moyens annuels. Cette agrégation réduit la pseudo-réplication des cellules-jours. Le test binomial exact des signes porte sur les années aux écarts non nuls. Chaque année contribue un signe, quel que soit son nombre de cellules. Sous H0, un écart positif a une probabilité de 0,5 parmi les années sans égalité. H1 est bilatérale. Le choix du test évite une hypothèse de normalité sur douze amplitudes annuelles.

{{APPARIEMENTS}}

Dans les deux analyses, les douze années vont dans le sens d’une température plus élevée et d’une humidité plus basse les jours positifs. Pour chaque variable, p brute = 0,00048828. Holm corrige les deux tests de chaque famille, avec p ajustée = 0,00097656. La sensibilité mensuelle réduit l’amplitude des différences. Elle réutilise les mêmes observations. L’indépendance des saisons demeure incertaine et les associations ne permettent aucune conclusion causale.

![Écarts annuels entre les jours avec et sans détection, après appariement par cellule et année. Source : entraînement 2012–2023.](figures/ecarts_annuels.png){width=74%}

\newpage

# Distributions et corrélations sur le train

![Distribution des variables observées selon la classe sur le train. La superposition des distributions limite la séparation par une mesure isolée.](figures/distributions_train.png){width=84%}

![Corrélations entre variables numériques du train. Des mesures météo liées peuvent transmettre une information similaire au modèle.](figures/correlations_train.png){width=68%}

# Évaluation chronologique

Le train couvre 2012–2023. Chaque pli interne valide une année entière de 2019 à 2023 et n’apprend que sur les années antérieures. Cette adaptation du K-Fold demandé empêche l’apprentissage sur des années futures. Son acceptation pédagogique reste à confirmer. Le choix interne maximise le F1 moyen de la classe 1 à seuil 0,50. Imputation médiane, standardisation et pondérations sont apprises sur le sous-ensemble d’apprentissage de chaque pli.

La validation 2024 compare ensuite les six modèles et les seuils 0,20, 0,35 et 0,50 par F1. À égalité, priorité au seuil le plus élevé puis à l’ordre alphabétique. La règle et les candidats étaient fixés avant cette comparaison. L’examen historique répété de 2024 limite l’indépendance de toute estimation sur cette saison. L’artefact gagnant et son seuil ont été gelés dans Git avant l’ouverture de 2025. Aucun réajustement sur 2012–2024.

\newpage

# Qu’apprend-on avec un K-Fold classique ?

Après le gel, nous avons exécuté GridSearchCV avec KFold à cinq plis mélangés (graine 42) sur les 104 979 lignes du train. Les six grilles, budgets d’apprentissage, pipelines et seuil de 0,50 sont ceux du benchmark. Chaque ligne participe une fois à la validation mélangée. Pour comparer les découpages, le tableau reprend pour chaque modèle les paramètres déjà gelés. Les deux premières colonnes donnent les F1 moyens sur les parties apprentissage et validation du KFold. La dernière reprend les validations annuelles du protocole principal.

{{KFOLD}}

Pour la forêt, le F1 en validation mélangée atteint 0,563 contre 0,430 en validation chronologique. L’écart va dans l’autre sens pour le SVM. Les plis mélangés partagent des années entre apprentissage et validation, y compris des mesures postérieures aux observations classées. Ils estiment la classification de lignes tirées de ce même ensemble de saisons. Le protocole principal mesure le transfert à une année ultérieure. La composition des cohortes et parfois les tailles d’apprentissage changent aussi. Les différences observées ne permettent pas d’isoler un biais unique.

L’écart apprentissage–validation de K-NN (environ 0,073) suggère une sensibilité aux observations d’apprentissage. GaussianNB obtient environ 0,507 des deux côtés. Des scores proches ne prouvent ni l’absence de sous-apprentissage ni la généralisation à un autre climat. Aucune décision de modèle ou de seuil ne découle de ce diagnostic.

# Expérience secondaire K-NN et ACP

Les deux notebooks du lot secondaire utilisent 25 entrées, dont la normale NDVI présente dans leurs listes locales. Le benchmark utilise 24 entrées. Dans un environnement distinct avec scikit-learn 1.9.0, la chaîne imputation, échelle, ACP à 95 % et K-NN avec 2 001 voisins a été rechargée. Ses 12 composantes donnent une Average Precision de 0,105225 sur les 8 423 lignes de 2024. Les notebooks reproduisent 0,1046 sans ACP et 0,1049 avec la rétention de 90 %. L’AP mesure ici la somme des précisions pondérées par les gains de rappel. Plusieurs réglages ont été examinés sur 2024. Le léger écart observé demande confirmation. Le modèle officiel, son schéma et sa décision restent ceux gelés avant 2025.

\newpage

# Variabilité entre saisons

{{PLIS}}

Chaque colonne annuelle donne le F1 obtenu en validant sur cette seule année au seuil 0,50. La moyenne accorde le même poids à chaque saison. L’écart-type décrit les cinq scores observés. Il ne constitue pas un intervalle de confiance. La population de cellules et la fréquence des positifs varient entre saisons. Ces différences peuvent modifier le F1 même avec les mêmes hyperparamètres.

# Effet du nombre de lignes

{{TAILLES}}

Expérience complémentaire postérieure au gel. Chaque taille utilise trois tirages stratifiés (42, 43 et 44), les paramètres publiés et la validation 2024 entière. Les temps sont des moyennes en secondes. La dispersion décrit ici les tirages sur une même saison. La calibration interne du SVM utilise les observations du sous-ensemble d’apprentissage, sans contrainte chronologique interne. Les cinq plis externes restent chronologiques. Ces mesures ne modifient aucune décision publiée.

\newpage

# Six familles et coût de recherche

**Zero-R** apprend la classe majoritaire et constitue le point de comparaison sans hyperparamètre. **GaussianNB** combine des distributions conditionnelles gaussiennes. Les corrélations météo fragilisent son hypothèse d’indépendance. Le lissage de variance explore 14 valeurs de 10⁻¹² à 10. La sélection retient 1. Le lot historique à sept candidats obtenait un F1 2024 de 0,176681 contre 0,173585 dans la grille étendue.

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

\newpage

# Changements entre entraînement et validation

![Climat et part positive de juin à octobre. Les bandes indiquent les quartiles des mesures par mois dans chaque cohorte.](results/post_freeze/development_profiles/comparaison_mensuelle.png){width=94%}

En août, la température maximale médiane est proche dans les deux cohortes (33,5 °C en entraînement et 33,7 °C en 2024). La part des détections passe pourtant de 46,0 % à 10,1 % dans les cellules-jours échantillonnées. Cette comparaison par mois montre pourquoi un changement de prévalence ne se réduit pas à une variation de température. Les blocs de coordonnées d’un degré, les effectifs mesurés et les quantiles se trouvent dans *results/post_freeze/development_profiles/*.

**Erreurs du SVM en 2024 au seuil gelé de 0,20.** Les quartiles de température sont définis sur le train. Les colonnes comptent les vrais positifs, faux positifs, faux négatifs et vrais négatifs par intervalle.

{{TEMPERATURE}}

Dans la tranche la plus chaude, le modèle retrouve 244 des 248 détections, avec 2 015 fausses alertes. Dans la plus fraîche, il en retrouve 10 sur 73. La saison, la géographie et les autres variables liées à la chaleur peuvent contribuer à ces écarts. L’analyse décrit une seule saison de validation.

\newpage

# Du choix sur 2024 au résultat final sur 2025

Le SVM au seuil 0,20 obtient un F1 de 0,176646 sur la validation utilisée pour le sélectionner. Au seuil 0,35, il obtenait 0,175832. Malgré ces F1 proches, descendre de 0,35 à 0,20 retrouve 216 détections supplémentaires pour 2 216 fausses alertes supplémentaires. Le modèle de 3 500 observations a été conservé à l’identique, avec vérification des empreintes SHA-256 de l’artefact, de la configuration et du CSV avant l’évaluation.

**Validation 2024, 643 détections sur 8 423 observations.** Les trois seuils proviennent du protocole.

{{ALERTES}}

Pour les 1 258 scores de la tranche ]0,4 ; 0,5], le score moyen atteint 44,7 % et la fraction positive observée 10,3 %. Cette comparaison décrit la fiabilité sur la saison ayant servi à la sélection. Une calibration indépendante demanderait une autre cohorte de développement.

**Test final 2025, résultat publié au seuil gelé de 0,20.**

{{TEST}}

![Détections et alertes du SVM gelé, seuil 0,20. Source : évaluation finale 2025.](docs/confusion_2025.png){width=47%}

Sur 100 alertes émises, environ 16 correspondent à une détection étiquetée. Le résultat concerne la population échantillonnée. À titre de repère descriptif, annoncer une détection sur chaque ligne donnerait un F1 de 0,234 contre 0,263 pour le SVM.

Sur 8 467 lignes, le résultat final comprend **900 vrais positifs, 222 faux négatifs, 4 814 faux positifs et 2 531 vrais négatifs**. La hausse du F1 intervient dans un échantillon comptant davantage de positifs (13,3 %). La ROC-AUC reste modeste. Cette expérience soutient une classification rétrospective exploratoire. Une alerte opérationnelle demanderait des mesures connues à l’avance, une évaluation prospective et une estimation des coûts des erreurs.

\newpage

# À quoi le modèle attribue-t-il le score d’une observation ?

La page SHAP explique le score de la classe avec détection. Le point de départ est le score moyen du modèle sur un fond de vingt observations complètes du train. Une contribution positive augmente le score par rapport à cette référence. Le graphique individuel en cascade relie la base au score obtenu pour la cellule-jour. La vue globale résume l’amplitude et le sens des contributions sur des observations complètes de validation 2024.

![Explications de scores dans la page SHAP de Wildfire Atlas.](docs/reevaluation/shap-integration.png){width=86%}

Pour l’arbre et la forêt, TreeExplainer calcule les contributions en tenant compte de la structure des arbres et du fond choisi, en espace de probabilité. Pour les six autres pipelines, deux permutations des variables et leurs parcours inverses approximent les contributions. La somme peut restituer le score avec précision alors que la répartition entre variables dépend des permutations. [Méthode de Shapley appliquée aux prédictions](https://arxiv.org/abs/1705.07874).

Sur 25 observations de validation tirées avec la graine 42, l’écart absolu maximal entre le score positif et la base augmentée des contributions atteint 6,78 × 10⁻⁸ pour l’arbre, 1,80 × 10⁻⁸ pour la forêt et au plus 3,33 × 10⁻¹⁶ pour les six autres modèles. Les 25 observations ne contiennent qu’une détection, et le fond en contient quatre. Un classement global sur cet échantillon possède donc une portée limitée. Les températures corrélées partagent de l’information et le masquage peut combiner des valeurs peu plausibles. Ces contributions décrivent la réponse du modèle à la référence choisie.

\newpage

# Application, contributions et reproduction

![Wildfire Atlas. La carte regroupe les cellules-jours observées par cellule.](docs/interface-bureau.png){width=78%}

Command Center synthétise la couverture. Data Explorer partage les filtres entre statistiques descriptives, données manquantes, histogramme/KDE, fréquences, corrélations et export. Geo Intelligence contrôle les coordonnées. Model Arena rattache scores, courbes et matrices à leurs fichiers d’expérience. Prediction Studio conserve les mesures pendant la navigation et affiche le résultat correspondant au modèle, au seuil et aux entrées soumis. Model Arena présente les fausses alertes par mois et par seuil en 2024, puis le résultat publié sur 2025 dans une vue distincte. Le studio accepte également un CSV de 24 mesures par ligne et exporte les scores dans l’ordre du fichier. Scientific Insights présente le protocole et les tests appariés.

IASD17 a livré l’explicabilité SHAP, les bandes de score et son parcours de prédiction par lot. SIAD03 a intégré et vérifié ces fonctionnalités avec le contrat commun. Le dépôt collectif apporte les observations, le cadrage et un arbre historique. Le lot SIAD03 comprend audit, nettoyage, statistiques, EDA, Zero-R/NB et interface. La branche d’intégration SIAD03 ajoute les recherches K-NN, SVM, forêt et arbre compatible, le gel du modèle et ce rapport, avec assistance de développement. Le lot secondaire K-NN et ACP reste attribué à son auteur dans l’historique Git.

Depuis la racine, installer `requirements-dev.txt` sous Python 3.12. Lancer `python -m pytest -q` puis `python -m streamlit run src/app.py`. La commande `python -m src.models --output results/local_runs/benchmark` répète le développement dans un dossier neuf. Le README décrit la reproduction séparée du test gelé et de ce PDF. Les prédictions, paramètres par pli, versions et empreintes sont disponibles dans *results/benchmark_final/*.

**Conclusion.** Le transfert entre saisons et le coût des faux positifs dominent la lecture du résultat. Une utilisation prospective demanderait de connaître les mesures au moment de l’alerte et de suivre les performances sur une nouvelle cohorte.

**Références.** [Cahier du mini-projet](https://github.com/hosniadilemp-a11y/DataMiningProjectPage) · [Dictionnaire du producteur](https://github.com/Abdelmalek05/fire-detection-model/blob/0755f4e47f54a9e582b4f53d28f2a610098bbf1c/docs/DATASET.md) · [Jeu de données](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days) · [Validation croisée scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html) · [Test binomial exact SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html). Données sous CC BY 4.0, attributions complètes dans *docs/SOURCES.md*.
