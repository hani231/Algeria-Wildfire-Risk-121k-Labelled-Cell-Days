# Audit et sélection des améliorations SIAD03 — 16 novembre 2026

## Sources et portée

Base du dépôt original : `ebd4bf476bf9a09d3abe92e9685c42bc36ed6378`.
Les corrections et extensions scientifiques précédentes sont déjà fusionnées dans cette base.
Historique, branches distantes, scripts, notebooks 01/03, résultats, dictionnaire,
README, tests et plan de répartition ont été inspectés. Le plan (pages 3, 4, 9–11)
attribue à SIAD03 l'audit/nettoyage, l'EDA, les analyses statistiques, Zero-R et NB.
Les auteurs Git des modules de ce périmètre concordent avec cette attribution.
Les responsabilités inconnues sont protégées. Cette intervention ajoute uniquement
`src/siad03_nb`, `tests/siad03_nb`, `results/siad03_nb` et `docs/siad03_nb`.
Tous les fichiers préexistants sont conservés à l'identique, y compris le protocole,
le prétraitement, les modèles, les notebooks, l'application et le README collectif.

Sources consultées :
- [Site du cours et grille détaillée](https://hosniadilemp-a11y.github.io/DataMiningProjectPage/), source HTML publique consultée le 16 novembre 2026.
- Plan de répartition local, pages 3 et 11 ; document interne nominatif, à ne pas republier comme livrable.
- [Dépôt modèle](https://github.com/hosniadilemp-a11y/DataMiningProjectExample), commit `cf394821502d428478d4c07aa9e5785e1c98916b`.
- [Suivi du professeur](https://tp-dm.onrender.com/project-progress) : accès bloqué au tunnel proxy (403). Aucune note ni liste de promotion n'a pu être vérifiée. L'ajout du domaine a été enregistré dans le brouillon réseau, pas activé par cette action.

Les quatre autres PDF nommés dans la demande ne sont pas joints. Le PDF du dépôt
modèle est accessible et son texte a été consulté ; il n'est pas assimilé sans preuve
au fichier `Rapport_MiniProject (1).pdf` mentionné. La grille /20 du site et les poids
10/4/3/3 concordent avec la demande. Le site présente aussi une formule globale /18,
à clarifier avec l'enseignant ; aucun calcul de note finale n'est effectué ici.

## Référence disponible, pas classement des meilleurs étudiants

Le dépôt modèle indique explicitement être une démonstration avec contributions
simulées. Sa note est inconnue. Ses README, scripts de prétraitement/modélisation,
statistiques, tests, arborescence de notebooks/application et rapport PDF ont été
inspectés en lecture seule. Il n'a pas été exécuté : ses performances restent des
résultats publiés par l'auteur, non reproduits pendant cette intervention.

Points transférables : commande d'entraînement, résultats structurés, hypothèses et
tailles d'effet, figures, guide de reproduction, rapport. Limites : données médicales,
9 000 lignes annoncées alors que la règle explicite demande 10 000 ; CV stratifiée
aléatoire et F1 pondéré non transposables à nos années et F1 de la classe 1.
Le script `src/models.py` peut sous-échantillonner à 1 000 lignes, ce qui demande de
vérifier la provenance exacte des scores présentés. Aucun code n'est copié, aucun
historique de contributions simulées n'est reproduit et aucune causalité entre
fonctionnalités et notes n'est supposée.

## Audit comparatif et classement

L'état est celui de la base avant cette intervention. Gain qualitatif = contribution
à la conformité, pas attribution de points.

|Critère exact|Référence inspectée|Notre projet / état|Écart et amélioration|Responsable|Priorité|Gain|Complexité / risque|
|---|---|---|---|---|---|---|---|
|1.1 Prétraitement (2)|Pipeline et types distincts|Nettoyage testé, dictionnaire complet ; provenance incomplète|Confirmer unités et disponibilité historique ; ne pas inventer|SIAD03 + responsable protocole|Élevée|Rigueur|Moyenne / dépend du producteur|
|1.2 EDA/statistiques (3)|Six hypothèses, correction multiple et effets|Deux analyses appariées annuelles, Holm, sensibilité mensuelle, cartes ; présentes|Déjà satisfaisant dans le périmètre ; dépendance interannuelle explicitée|SIAD03|Moyenne|Interprétation|Faible / éviter multiplication des tests|
|1.3 Modèles (1)|Six algorithmes annoncés et scripts présents|Zero-R/NB/arbre et deux extensions présents ; K-NN/SVM/RF absents au HEAD|Modèles obligatoires manquants à fournir par leurs responsables|Responsables modèles communs|Critique|Complétude|Élevée / protégé|
|1.4 Optimisation/CV (2)|Grilles et CV stratifiée|NB sept valeurs, optimum 0.01 à la borne ; entraînement notebook incomplet pour CLI|Commande personnelle ; étendre la grille ; garder cinq plis annuels|SIAD03|Élevée|Reproductibilité et exploration justifiée|Moyenne / faible|
|1.5 Métriques (2)|ROC/confusions et tableaux|AP, ROC, F1, calibration, bootstrap, erreurs déjà présents|Ajouter traçabilité et diagnostics spécifiques de la nouvelle grille NB|SIAD03|Élevée|Résultats vérifiables|Faible / résultat 2024 exploratoire|
|2.1 Architecture (1.5)|Application avec navigation|Démos présentes ; application principale absente|Intégration collective requise, aucune refonte ici|Responsable application|Critique|Fonctionnalité|Élevée / protégé|
|2.2 Dashboard (1)|Pages EDA|Six éléments, filtres, cas vide, cartes ; fonctionnel sous AppTest|Conserver ; pas de tableau de bord concurrent|SIAD03 / intégrateur|Faible|Prévenir régression|Faible|
|2.3 Prédiction (1.5)|Formulaire présent dans le code|Formulaire commun absent|Interface et pipeline commun à livrer par leurs responsables|Responsables protocole/application|Critique|Fonctionnalité|Élevée / protégé|
|3.1 Structure (1)|data/src/notebooks/docs/tests|Présente ; scripts NB hors notebook manquants|Ajout isolé sans réorganisation|SIAD03|Moyenne|Maintenabilité|Faible|
|3.2 Contributions (2)|Contributeurs simulés explicitement|Trois auteurs historiques ; commits authentiques|Commits par sujet, identité existante, PR à relire|Chaque membre|Élevée|Traçabilité|Faible|
|4.1 Rapport (1.5)|PDF disponible|Rapport personnel existant ; rapport collectif absent|Annexe NB sourcée ; assemblage réservé|SIAD03 / intégrateur|Élevée|Reproductibilité scientifique|Moyenne|
|4.2 README (1.5)|Guide et chiffres publiés|README substantiel ; guides existants|Guide complémentaire autonome, pas d'écrasement du partagé|SIAD03 / intégrateur|Moyenne|Exécution|Faible|

## Décisions

Retenus : garde-fous du contrat, CLI Zero-R/NB, grille 14 valeurs (70 ajustements CV
NB + réajustement final), conservation des prédictions/empreintes/versions, diagnostics,
tests de reproduction, annexe scientifique. L'imputation et la standardisation restent
celles de l'expérience NB initiale et sont apprises dans chaque pli. Aucun pipeline
commun n'est redéfini ; la fonction de plis existante est importée en lecture seule.

Non retenus : nouvelles cartes ou nouveaux tests statistiques redondants ; tuning sur
2024 ; SMOTE sans justification temporelle ; nouveaux modèles hors périmètre ; changements
du protocole commun. Le statut `proposition_a_harmoniser` reste visible.

## Protection et anonymat

Les nouveaux textes publics utilisent SIAD03, pas les prénoms ni les adresses des
étudiants. L'identité Git reste l'identité réelle confirmée (pas de réattribution).
L'anonymat global n'est pas satisfait : le PDF de répartition et des noms de fichiers
historiques restent nominatifs. Ces fichiers préexistants/protégés ne sont pas effacés
ni réécrits. L'équipe doit préparer une version publique anonymisée et confirmer les
codes des autres membres avant le rendu. Aucune garantie de note n'est donnée.
