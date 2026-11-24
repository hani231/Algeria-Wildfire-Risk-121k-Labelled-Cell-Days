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

## Recette de réévaluation

Sur un même navigateur, choisir le SVM dans Prediction Studio, modifier le jour de l’année, calculer la classe puis visiter une autre page et revenir. Les champs, le modèle et la classification soumise doivent être conservés. Après modification d’une valeur, relancer « Prédire » pour obtenir le résultat de la nouvelle observation. Ces données sont propres à la session Streamlit.

Dans Model Arena, « Comparaison 2024 » présente les modèles au seuil commun de 0,50. « Test final 2025 » lit le résultat enregistré du SVM à 0,20. Les deux taux répondent à des questions différentes : combien de positifs sont retrouvés et combien d’alertes correspondent à un positif. Dans Data Explorer, chaque coefficient de Spearman requiert au moins trois observations communes et deux variables non constantes.

Captures réelles du panneau de test publié, sur trois largeurs : [ordinateur](reevaluation/arena-bureau.png), [tablette](reevaluation/arena-tablette.png), [téléphone](reevaluation/arena-mobile.png).

## Importer plusieurs cellules-jours

1. Ouvrir Prediction Studio, choisir un pipeline, puis « Fichier CSV ». Le seuil affiché s’applique à chaque ligne.
2. Télécharger l’exemple. Conserver les 24 noms de colonnes, dans l’ordre souhaité. Utiliser les unités du formulaire, un point pour les décimales et la virgule entre champs. Chaque observation doit être complète et dans les plages du train affichées par le formulaire individuel. [Dictionnaire des unités](dictionnaire_colonnes.md)
3. Importer le fichier UTF-8 (1 Mio, 1 000 observations au maximum). Une erreur de schéma, de plage ou de cohérence interrompt le lot entier. Corriger le fichier avant de le soumettre à nouveau.
4. Vérifier le nombre d’alertes et exporter. La colonne `observation` numérote les lignes du fichier à partir de 1. L’export conserve les mesures, le nom du pipeline, son seuil, la classe et le score. L’inférence s’exécute en mémoire avec le pipeline sauvegardé.

Dans Model Arena, « Alertes du SVM en 2024 » présente les trois seuils au niveau de la saison et les erreurs mensuelles au seuil retenu. Dans le tableau de fiabilité, comparer le score moyen à la fraction positive du même intervalle et lire l’effectif avant d’interpréter l’écart.
