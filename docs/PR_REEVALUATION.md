## Objet

Intégrer à la version collective de Wildfire Atlas les huit commits de la réévaluation SIAD03 et les six commits d’origine de la branche IASD17. La branche part du collectif da93591. Les corrections de la revue concernent le studio, l’explicabilité, la comparaison entre saisons de développement et les preuves du rapport.

## Éléments à relire

- **ML et statistiques (1.1 à 1.5).** Les profils mensuels du train et de 2024 couvrent météo, indices de feu et végétation. Au seuil SVM de 0,20, les 2 299 cellules-jours au-dessus de 34,2 °C comprennent 244 détections retrouvées et 2 015 fausses alertes. Les six grilles du benchmark, les scores de validation et les pièces du gel de 2025 ont été contrôlés.
- **Application (2.1 à 2.3).** Le studio valide et borne les imports, écarte les métadonnées de résultat à la réimportation et distingue la classe des tranches de score. Dans l’espace d’explicabilité, le beeswarm trace les observations, le fond provient du train et la somme des contributions est comparée au score de classe 1. Avec quatre ordres de permutation, les contributions par variable restent approximatives.
- **Git (3.1 et 3.2).** Le merge 5087612 conserve les deux historiques. La CI installe les versions déclarées sous Python 3.12 sur Ubuntu et Windows. La matrice du README relie les rôles aux livraisons.
- **Rapport et documentation (4.1 et 4.2).** Le PDF comprend les résultats sur le changement de population, la figure de validation, une capture réelle du parcours SHAP et les limites scientifiques. Le README explique la reproduction et la vérification des chiffres.

## Validation locale

234 tests réussis, huit modèles contrôlés, six notebooks rejoués en copie isolée. Le contrôle du PDF relit 11 tableaux et 49 lignes numériques. Les parcours Chromium couvrent les sept espaces, la persistance des sélections, les trois figures SHAP et l’export-réimport CSV à trois largeurs. Aucune nouvelle inférence n’a été exécutée sur le test 2025.

## Décisions de l’équipe

Confirmer le code étudiant de l’auteur du lot K-NN/ACP, vérifier le poste de soutenance et recueillir l’avis pédagogique sur la sélection chronologique. La règle finale reste celle du SVM gelé au seuil 0,20. Une fois la version retenue, transmettre le SHA et le rapport de ce commit au professeur.

[Audit et checklist](https://github.com/lyesaitikhlef/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/blob/improvement/siad03-final-reevaluation/docs/AUDIT_FINAL_REEVALUATION.md)
