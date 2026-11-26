# Revue de l’explicabilité IASD17

La branche IASD17 au commit `56c9285` apporte la page d’explicabilité, l’explication locale de la dernière soumission et les premiers tests sur huit modèles. Cette revue SIAD03 porte sur la version intégrée, avec Python 3.12 et SHAP 0.54.1. Les explications ont pour cible le score de la classe « détection » du pipeline sérialisé.

## Anomalies reproduites et corrections

| Vérification sur la branche d’origine | Observation | Correction vérifiée |
|---|---|---|
| Affichage du beeswarm, cinq lignes de validation | Le titre et les axes apparaissaient, avec zéro point. La fonction `summary_plot` attend `plot_type='dot'`. | Test Streamlit qui compte les points sur l’axe du graphique effectivement affiché. |
| Fond annoncé de 20 cellules-jours pour l’arbre | TreeExplainer prenait sa référence dans les chemins de l’arbre. Base mesurée 0,50000 pour une moyenne de 0,33656 sur le fond annoncé. | TreeSHAP utilise le fond transformé par le préprocesseur gelé et calcule des contributions au score de classe 1 pour cette référence empirique. |
| Permutations pour GaussianNB, deux appels sur les cinq mêmes lignes | Écart maximal de 0,02093 entre les contributions. La graine du tirage du fond ne pilotait pas les permutations. | Deux ordres pseudo-aléatoires et leurs inverses sont fixés avec un générateur local. Une même observation reçoit les mêmes contributions, seule ou au sein d’un lot réordonné. |
| Cohorte, schéma et sélection de classe | Le chargeur UI séparait déjà le train de 2024. La fonction de tirage acceptait indépendamment une cohorte quelconque. La branche arbre utilisait l’index de sortie 1. | Contrôle explicite des années et du split lors du tirage, schéma ordonné et recherche de l’index de la classe positive. Un exemple linéaire de solution connue teste les contributions par variable avec un ordre de classes inversé. |

## Définition et portée

Le fond est un tirage uniforme, graine 42, de 20 lignes parmi les 104 924 observations complètes du train (104 979 au total). Il contient quatre jours positifs. La vue par défaut explique 25 lignes parmi les 8 420 complètes de validation 2024 (8 423 au total). Le tirage de 25 avec la même graine contient un positif. Ces deux petits échantillons permettent l’interaction. Les observations incomplètes et certains régimes géographiques ou météorologiques y sont absents. Les graphiques globaux résument strictement les lignes sélectionnées.

Pour un ensemble de variables observées, la valeur de la coalition est le score moyen obtenu en complétant les autres mesures avec les lignes du fond. Les deux arbres emploient TreeSHAP dans son mode interventional, en sortie probabilité. Les transformations de leurs pipelines conservent les 24 dimensions et leur ordre. Les six autres modèles utilisent les différences marginales de score le long de quatre chemins de permutation. La fonction forme un lot des valeurs intermédiaires pour une observation à la fois, puis moyenne les contributions. La classe s’obtient séparément en appliquant le seuil du pipeline.

L’égalité additive est un contrôle de cohérence numérique. Pour les permutations, elle découle de la somme télescopique sur chaque chemin et laisse subsister une incertitude sur l’attribution individuelle. Avec des variables corrélées, les observations hybrides peuvent combiner des valeurs météo incompatibles. L’importance moyenne dépend du fond, du modèle, des observations et de l’ordre des permutations. Une importance élevée ne démontre aucun effet causal.

## Résultats sur les huit artefacts

Mesures sous Linux, un processus neuf par modèle, un fil de calcul, mêmes 25 observations complètes 2024 et même fond de 20. Le temps couvre la création de l’explicateur et le calcul des 25 décompositions après chargement des données et du modèle. La mémoire est le pic résident du processus entier, dépendances et chargement des cohortes inclus, mesuré par `resource.getrusage`. Les chiffres de temps et de mémoire dépendent de la machine.

| Pipeline | Écart maximal entre score et somme | Durée (s) | Pic (Mio) |
|---|---:|---:|---:|
| Arbre de décision | 6,78 × 10⁻⁸ | 0,01 | 551 |
| Random Forest | 1,80 × 10⁻⁸ | 0,09 | 552 |
| Zero-R | 0 | 0,07 | 585 |
| GaussianNB | 3,33 × 10⁻¹⁶ | 0,09 | 587 |
| SVM | 2,22 × 10⁻¹⁶ | 1,58 | 553 |
| K-NN | 5,55 × 10⁻¹⁷ | 2,26 | 591 |
| Régression logistique | 3,33 × 10⁻¹⁶ | 0,09 | 587 |
| HistGradientBoosting | 2,22 × 10⁻¹⁶ | 0,26 | 551 |

Sur les huit modèles, l’écart maximal entre la base et le score moyen du fond est de 3,77 × 10⁻¹⁵. Pour le SVM, en gardant observations et fond fixes mais en passant de la graine 42 à 7 pour les permutations, les trois premières variables par contribution absolue moyenne restent FWI, jour de l’année et température moyenne. L’écart absolu moyen entre les 600 contributions atteint 0,00244 et le maximum individuel 0,10832. Une lecture au centième d’une contribution locale demanderait davantage de permutations et plusieurs fonds.

## Reproduction

Installer les dépendances depuis la racine, puis lancer `python -m pytest -q tests/test_shap_backend.py`. Les tests vérifient notamment les huit sorties, la moyenne du fond, le non-réentraînement, le waterfall et le contenu du beeswarm. Pour reproduire la comparaison numérique sur les 25 lignes utilisées dans le tableau, exécuter dans le même environnement :

```python
import numpy as np
from src.explainability.shap_backend import make_explainer, sample_background
from src.ui.services import ARTIFACTS, pipeline, training
from src.ui.shap_page import validation

for name in ARTIFACTS:
    model = pipeline(name)
    features = list(model.feature_names_in_)
    reference = sample_background(training(), features)
    sample = validation()[features].dropna().sample(25, random_state=42)
    exp = make_explainer(model, reference)(sample)
    scores = model.predict_proba(sample)[:, list(model.classes_).index(1)]
    print(name, np.abs(scores - (exp.base_values + exp.values.sum(axis=1))).max())
```
