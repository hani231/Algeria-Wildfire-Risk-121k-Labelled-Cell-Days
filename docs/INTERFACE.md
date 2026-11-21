# Wildfire Atlas

Avec Python 3.12, depuis la racine du dépôt sous Windows PowerShell :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```

Ouvrir l’URL locale affichée dans le terminal. Depuis un environnement Python activé, la commande de lancement est `python -m streamlit run src/app.py`.

| Espace | Travail proposé |
|---|---|
| Command Center | Situer les observations sur la carte, consulter la couverture du CSV et suivre les deux classes par saison d’entraînement. |
| Data Explorer | Filtrer années, mois, zones, classes et plage météo. Examiner les distributions, les valeurs manquantes et les corrélations, puis exporter la sélection. |
| Geo Intelligence | Ajuster la période, survoler une cellule, zoomer et consulter ses coordonnées et ses effectifs dans le tableau. |
| Model Arena | Classer les modèles par métrique sur 2024 et examiner confusion, courbes et réglages. |
| Prediction Studio | Sélectionner le pipeline, renseigner les groupes de mesures et lire la classe et la probabilité après soumission. |
| Scientific Insights | Consulter le protocole, les contrôles du CSV et la comparaison des températures et humidités avec ou sans appariement mensuel. |

## Données et limites

Les cartes agrègent les coordonnées observées par cellule. Le rayon représente le nombre de cellules-jours, la couleur la part des observations avec détection. Les contours de contexte proviennent du jeu de données public Natural Earth [Admin 0, 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson). Ils sont fournis localement et leur résolution limite la précision du littoral.

Conserver le CSV brut dans Dataset/, le protocole dans config/ et les lots versionnés dans results/. Le studio charge huit pipelines. Les six obligatoires viennent de benchmark_final, les deux supplémentaires du benchmark historique. L’arbre a été réentraîné avec scikit-learn 1.8.0. Le tableau comparatif porte sur 2024 à seuil 0,50. Le studio applique le seuil final 0,20 au SVM. Le rapport présente l’évaluation sur 2025.

## Organisation

L’entrée Streamlit est src/app.py. Le module src/ui/shell.py porte la navigation, atlas.css les styles, geography.py la carte, pages.py la synthèse et le protocole, model_pages.py les espaces modèles et prédiction. Les données et les artefacts sont chargés par services.py. Les distributions et corrélations sont partagées avec la démo autonome dans src/eda_view.py.

[Ordinateur](interface-bureau.png) · [Tablette](interface-tablette.png) · [Mobile](interface-mobile.png)

## Vérifier une observation et un résultat

Les sélections de Data Explorer sont conservées pendant la navigation. « Réinitialiser les filtres » rétablit l’ensemble du train. Le survol d’une case de Spearman indique le nombre de paires complètes. L’histogramme affiche son effectif échantillonné.

Model Arena distingue les six classifieurs demandés et les deux supplémentaires. Pour GaussianNB, le classement et les courbes utilisent le benchmark final qui reproduit run_01 (F1 0,173585). Le benchmark antérieur obtenait 0,176681. L’accuracy de Zero-R atteint 92,37 % en classant toutes les lignes en 0, avec 643 détections manquées.

Dans le studio, les libellés précisent les unités établies ou signalent leur incertitude. Une incompatibilité de version ou de schéma interrompt le chargement. Les contrôles sur les entrées précèdent la classification. Les probabilités concernent la classe de l’observation dans cet échantillon.

## Recette avant la soutenance

1. Lancer l’application sur le poste de présentation. Ouvrir les six espaces, puis répéter en écran étroit. Vérifier que les tableaux restent accessibles et que le formulaire peut être soumis.
2. Dans Exploration, sélectionner une année et un mois, vérifier l’effectif et exporter. Réinitialiser les filtres et comparer au total du train.
3. Dans Carte, retirer tous les mois, puis en sélectionner un. Vérifier le message pour une sélection vide et le retour des cellules sur la carte.
4. Dans Modèles, comparer les F1 sur 2024 au seuil 0,50, puis afficher la matrice et les courbes du SVM. Dans Prédiction, vérifier le seuil 0,20 avant et après avoir soumis l’exemple.
5. Dans Méthodologie, comparer l’appariement annuel et mensuel. Les graphiques doivent suivre la sélection. Noter le navigateur et la largeur d’écran effectivement utilisés.
