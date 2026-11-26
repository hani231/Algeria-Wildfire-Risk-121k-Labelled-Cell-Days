# Recette de Wildfire Atlas sur Chromium

La recette du 26 novembre 2026 a utilisé Python 3.12 sous Linux et un navigateur Chromium 156.0.8078.79 piloté par Playwright. Elle a porté sur les interactions et le contenu effectivement rendu. Les contrôles numériques indépendants des huit modèles figurent dans les tests du benchmark et de l’explicabilité.

## Rejouer le parcours

Depuis la racine du projet et l’environnement décrit dans le README, lancer `python -m streamlit run src/app.py`. Ouvrir l’adresse locale dans une nouvelle session du navigateur et effectuer les opérations ci-dessous.

| Parcours | Opération et résultat observé |
|---|---|
| Accueil et navigation | Depuis Command Center, les six autres espaces s’ouvrent, dont Geo Intelligence et Scientific Insights. |
| Data Explorer | Les statistiques, valeurs manquantes, fréquences, histogramme avec densité et corrélations se consultent dans les trois onglets. Vider le filtre Classes affiche le message d’absence d’observations. En passant par la carte puis en revenant, le filtre reste vide. Réinitialiser restaure les statistiques. |
| Model Arena | Consulter les fausses alertes du SVM sur 2024, sélectionner ensuite le test publié 2025 et visiter le studio. Au retour, le résultat 2025 reste sélectionné. |
| Prediction Studio | Soumettre les valeurs initiales du formulaire individuel. La classe estimée reste consultable après un aller-retour par l’explicabilité. |
| Explainability | Avec DecisionTree et 25 observations complètes de validation, les deux figures globales s’affichent. La troisième figure explique la dernière observation soumise dans le studio, ici avec GaussianNB. Le waterfall affiche une base de 0,3385 et un score reconstruit de 0,2000, égal au score du modèle à la précision affichée. [Capture du rendu global](reevaluation/shap-integration.png) |
| Lot CSV | Télécharger l’exemple, l’importer, exporter sa classification puis réimporter l’export. Les deux exports sont identiques octet par octet. Remplacer le lot par un CSV ne contenant que `label` et `sample_kind` affiche une erreur de schéma et retire le téléchargement du résultat précédent. |
| Écrans étroits | Sur le lot CSV, la largeur du document respecte les fenêtres de 1 440 × 1 040, 900 × 1 024 et 390 × 844 pixels. En session mobile émulée à 390 pixels, les commandes du menu permettent aussi de rejoindre Explainability, Prediction Studio et Geo Intelligence. |

Le parcours intégré s’est terminé sans exception JavaScript observée. Sur le `main` collectif initial `da93591`, le passage par une autre page faisait revenir Model Arena de « Test final 2025 » à « Comparaison 2024 ». Le test de régression conserve maintenant la cohorte, le modèle SHAP et la taille de l’échantillon après navigation. La commande `python -m pytest -q tests/test_navigation_final.py` a réussi (un test).

Les trois largeurs sont des fenêtres de Chromium sous Linux. L’équipe doit encore répéter le parcours sur le poste et le vidéoprojecteur de la soutenance.
