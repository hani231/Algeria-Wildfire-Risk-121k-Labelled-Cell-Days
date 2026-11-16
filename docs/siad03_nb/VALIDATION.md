# Validation et reste à faire

- Base existante : 47 tests réussis avant intervention.
- Suite complète après intervention : **69 réussis**, aucun échec ni test ignoré,
  cinq avertissements Seaborn de dépréciation ; 16,61 secondes sur cette machine.
- Le premier lancement global a révélé un conflit de noms entre `test_artifacts.py`
  dans deux dossiers. Le package `tests/siad03_nb` le corrige sans modifier les tests existants.
- Deux entraînements réels indépendants : métriques et prédictions 2024 identiques,
  grilles identiques hors colonnes de durée, modèles rechargés vérifiés.
- Découpage réel : 104 979 observations 2012–2023 et 8 423 observations 2024 ;
  les cinq validations couvrent 2019–2023 avec strict respect du passé.
- Trois fuites de cible exclues ; prédicteurs historiques supplémentaires non vérifiés
  également refusés. L'altération des valeurs du test n'influence pas les entrées.
- `pip check` réussi ; tests AppTest existants des deux dashboards réussis.
- Aucune modification/suppression d'un fichier présent à `ebd4bf4` ; uniquement des
  ajouts dans les quatre répertoires `siad03_nb`.
- Nouveaux livrables sans noms personnels ; anonymat du dépôt historique incomplet,
  document interne nominatif préexistant à traiter collectivement.
- Pas de réexécution des notebooks complets, pas d'essai Windows manuel, pas de nouvelle
  mesure sur 2025. Aucun test du dépôt modèle externe n'est présenté comme exécuté.

## Travaux réservés aux collaborateurs

Responsable prétraitement/protocole : confirmer le protocole encore proposé, fournir
le pipeline partagé, K-NN/SVM et fonction de prédiction ; relire le contrat utilisé
par l'expérience NB et confirmer l'adaptation temporelle des cinq plis.

Responsable application/modèles : réentraîner l'arbre avec les versions communes,
implémenter Random Forest, assembler l'application et le formulaire, intégrer les
résultats personnels puis le rapport collectif. Le nouveau dossier ne remplace aucun
de ces éléments.

Collectif : confirmer provenance/unités et codes autorisés, préparer un rendu anonymisé,
geler tous les choix avant l'évaluation 2025. La comparaison aux projets notés reste
bloquée tant que la page de suivi n'est pas accessible ou que la liste n'est pas transmise.

## Estimation de conformité (pas une note)

|Critère|Maximum|Preuve|Niveau constaté / risque restant|
|---|---:|---|---|
|1.1 Prétraitement|2|Nettoyage, tests, dictionnaire ; pipelines NB dans les plis|Partiel collectivement : pipeline commun/provenance à confirmer|
|1.2 EDA/statistiques|3|Deux tests appariés, Holm, figures, analyse saisonnière existante|Solide dans le périmètre ; hypothèses de dépendance à expliciter|
|1.3 Modèles|1|Zero-R/NB/arbre présents, extensions supplémentaires|Partiel : trois algorithmes obligatoires manquent|
|1.4 Optimisation/CV|2|14 réglages NB, cinq plis, grille et sélection tracées|Solide pour NB ; autres modèles et accord protocole requis|
|1.5 Métriques|2|Confusions, F1, AP, ROC, erreurs, calibration, reproduction|Solide pour modèles disponibles ; synthèse collective incomplète|
|2.1 Architecture/stabilité|1.5|Deux démos testées|Partiel : application principale absente|
|2.2 Dashboard EDA|1|Six éléments et cas vides testés|Fonctionnel ; intégration collective restante|
|2.3 Prédiction interactive|1.5|Formulaire commun absent|Non satisfait au HEAD ; hors périmètre|
|3.1 Structure|1|Arborescence et dépendances conservées|Présente ; nouveaux modules isolés|
|3.2 Contributions|2|Historique réel et nouveaux commits personnels|Traçabilité présente ; régularité collective relève de l'enseignant|
|4.1 Rapport PDF|1.5|Rapport personnel existant et annexe NB|Partiel : assemblage collectif requis|
|4.2 README|1.5|README partagé conservé + guide autonome|Présent ; harmonisation finale par l'intégrateur|

Les maxima ne sont pas additionnés pour inventer une note. Le travail collectif
manquant ne peut pas être remplacé par l'ajout de graphiques ou de modèles optionnels.
