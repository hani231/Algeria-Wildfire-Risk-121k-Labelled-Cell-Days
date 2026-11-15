# Audit complémentaire SIAD03 — 15 novembre 2026

Base locale : `0b49805`. Branche initiale `work`, arbre propre, identité Git locale
existante vérifiée. Le remote pointe vers le fork personnel. Aucun historique réécrit.
Tous les fichiers suivis à cette base sont protégés dans cette intervention ; seules
les nouvelles extensions sont modifiées. Aucun push ni fusion automatique.

Sources relues : scripts, deux notebooks (code), CSV, protocole et résultats, historique,
README et documentation. Les tests sont exécutés, pas simplement inventoriés.
Le site officiel est consulté via `DataMiningProjectPage/main/index.html` sur GitHub.
Il confirme les poids 10/4/3/3, les six modèles, les six fonctionnalités EDA,
GridSearchCV/RandomizedSearchCV et K>=5. Il mentionne aussi un projet /18 dans une
formule globale : ne pas confondre celle-ci avec la grille analytique /20.
Le PDF de répartition est local ; les PDF du cahier des charges, du rapport modèle,
du cours et des TP ne sont pas joints à cette session. Les consultations historiques
mentionnées dans l'ancien audit ne sont pas présentées comme de nouvelles lectures.
La référence du site comporte six modèles, une application et un rapport ; nous ne
pouvons pas comparer page à page son PDF absent. Sa précision ne constitue pas une
cible transférable à ce problème à négatifs sélectionnés.

## État initial par critère

|Critère|État|Preuve / lacune|
|---|---|---|
|Prétraitement 2|Partiellement conforme|121869 x 37, nettoyage testé ; provenance et disponibilité temporelle incomplètes|
|EDA/statistiques 3|Partiellement conforme|6 fonctions et 2 tests appariés annuels ; hypothèse d'indépendance interannuelle non démontrée|
|Modèles 1|Partiellement conforme|Zero-R, NB, arbre présents ; K-NN, SVM, RF absents|
|Optimisation/CV 2|Partiellement conforme|NB 7 configurations, arbre 48, cinq plis chronologiques ; protocole encore proposé|
|Métriques 2|Partiellement conforme|3 modèles sur validation ; manque erreurs détaillées et calibration|
|Architecture 1,5|Non conforme|Application principale absente|
|EDA interactive 1|Conforme sous réserve des tests|Démo avec les 6 fonctions, tests AppTest existants|
|Prédiction 1,5|Non conforme|Formulaire absent, périmètre protégé|
|Structure 1|Conforme|src/data/notebooks/docs et dépendances|
|Contributions 2|Partiellement conforme|Historique réel ; nouveaux commits locaux à publier ultérieurement|
|Rapport 1,5|Non conforme|Rapport final collectif absent|
|README 1,5|Partiellement conforme|Guide substantiel mais projet incomplet|
|Provenance/anonymat|Partiellement conforme|Unités/construction non certifiées ; anciens supports nominatifs|

## Top 10 et décisions

Tous les nouveaux chemins sont sous `*/siad03_extensions/`, attribués à SIAD03.
Effort indicatif en heures, impact qualitatif, sans promesse de points.

|Rang/priorité|Amélioration / problème résolu|Barème|Fichiers|Effort|Impact / risque / compatibilité|
|---|---|---|---|---|---|
|1 P0|Compléter K-NN/SVM/RF et formulaire|1.3/1.4/2.1/2.3|Fichiers des responsables|8–20|Critique ; protégé, signalé seulement|
|2 P0|Garde-fous fuite/test/sorties|1.1/1.4|data.py, tests|1–2|Fort ; lecture du protocole sans changement|
|3 P1|Erreurs, PR, MCC, Brier, calibration|1.5|evaluation.py|2–3|Fort ; comparaison indépendante à seuil fixé|
|4 P1|Benchmark linéaire et boosting optimisés|1.3/1.4|benchmark.py|2–4|Fort ; 5 plis existants, coût borné|
|5 P1|Cartes avec dénominateurs et saisons|1.2/2.2|exploration.py, dashboard.py|2–3|Fort ; proportions échantillonnées seulement|
|6 P1|Dérive 2024 et couverture spatiale|1.2/1.5|exploration.py|1–2|Fort ; descriptive, sans test naïf par ligne|
|7 P1|IC par blocs géographiques|1.5|evaluation.py|1–2|Fort ; dépendance entre cellules demeure|
|8 P2|Permutation conditionnée au mois|1.5|explain.py|1–2|Moyen ; non causal, corrélations limitent l'attribution|
|9 P1|Rapport scientifique personnel PDF|4.1/4.2|rapport, README|2–3|Fort ; annexe à intégrer au rapport collectif|
|10 P2|Sensibilité mensuelle/statistique|1.2|analyses existantes|0,5|Déjà correcte : reproduire sans réinventer|

P3 différés : SHAP, six autres modèles, nouvelles variables non vérifiables,
calibration entraînée sur 2024, seuil optimisé sur 2024. Complexité ou risque de
surajustement sans avantage établi. Aucun modèle supplémentaire ne remplace les
algorithmes obligatoires manquants. Zero-R et NB existants sont conservés ; pas de
nouvelle recherche NB identique. Le F1 reste la sélection CV pour comparabilité ;
AP, ROC-AUC et calibration complètent son interprétation. Les fenêtres météo et NDVI
restent une limitation de classification rétrospective, pas une prévision opérationnelle.
