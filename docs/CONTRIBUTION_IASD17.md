# Contribution IASD17 — Studio avancé et explicabilité SHAP

> Document historique de la branche IASD17 au commit 56c9285. Les tests et libellés ci-dessous décrivent cette livraison. Les revues d’intégration détaillent le comportement livré pour la réévaluation. [Explications SHAP](REVUE_SHAP.md) · [Studio et CSV](REVUE_STUDIO.md)

**Auteur :** IASD17 · **Date :** 24 novembre 2026 · **Branche :** `feature/iasd17-streamlit-shap`
**Plan de référence :** [AUDIT_IASD17_PLAN.md](AUDIT_IASD17_PLAN.md) · **Environnement :** Python 3.12, `requirements-dev.txt` + `shap==0.54.1`

## Périmètre

| Mission | Livrable |
|---|---|
| A — Application Streamlit | Niveaux d'alerte multi-seuils, import CSV par lots, export des prédictions |
| B — Explicabilité | Page « Explicabilité » : beeswarm et barre globaux (SHAP), waterfall individuel branché sur le studio |
| C — Tests et documentation | 60 tests ajoutés (169 au total), fiche de contribution, INTERFACE et README mis à jour |

Aucun fichier tiers n'est réécrit : `model_pages.py` appelle les nouveaux modules, `services.py`, `models.py`, `preprocessing.py`, le protocole et les artefacts du benchmark restent inchangés.

## Mission A — Prediction Studio étendu

### Niveaux d'alerte (`src/explainability/alert_levels.py`)

Le score de classe est positionné sur les seuils de `config/protocole.json` (0,20 / 0,35 / 0,50) :

| Score | Niveau | Couleur |
|---|---|---|
| `< 0,20` | Faible | vert |
| `≥ 0,20` et `< 0,35` | Modéré | ambre |
| `≥ 0,35` et `< 0,50` | Élevé | orange |
| `≥ 0,50` | Critique | rouge |

Un badge coloré s'affiche sous la jauge après chaque prédiction, avec la position exacte sur les seuils. Le score reste une probabilité de classe **rétrospective** sur une cellule-jour de l'échantillon : il ne mesure pas le risque futur sur le territoire.

### Studio avancé (`src/ui/prediction_enhanced.py`)

Section « Studio avancé » sous le formulaire du studio :

1. **Modèle de colonnes** : téléchargement d'un CSV d'en-têtes du protocole avec une ligne d'exemple issue du train.
2. **Import CSV** : `file_uploader` acceptant un CSV d'observations.
3. **Contrôle** : 24 colonnes du protocole présentes **dans l'ordre exact**, valeurs numériques finies (les manquantes sont imputées par le pipeline comme à l'entraînement), pas d'infini, cohérence physique (`coherence_counts`), colonnes de jours entières, `doy` ∈ [1, 366]. Colonnes manquantes, ordre invalide, valeurs non numériques ou incohérences → message précis (colonne et position).
4. **Prédiction en lot** : colonnes ajoutées `score`, `prediction`, `alerte` (quatre niveaux), distribution des alertes en métriques, aperçu du tableau.
5. **Export** : `download_button` produisant un CSV relisible par `read_csv`.

Les colonnes supplémentaires (identifiants, dates) sont conservées dans l'export mais ignorées pour la prédiction.

## Mission B — SHAP sur les huit pipelines

### Stratégies (`src/explainability/shap_backend.py`)

| Modèles | Explainer | Justification |
|---|---|---|
| DecisionTree, Random Forest | `TreeExplainer` (classe 1) | exact, quasi instantané |
| Zero-R, GaussianNB, K-NN, SVM, LogisticRegression, HistGradientBoosting | `PermutationExplainer` sur `predict_proba[:, 1]` | model-agnostic, additivité garantie |

- **Additivité vérifiée** sur les huit pipelines : `base + Σ contributions = predict_proba(classe 1)` (test paramétré, écart < 1e-6).
- **Aucun réentraînement** : seule l'inférence du pipeline figé est appelée (test de non-réentraînement).
- **Fond** : 20 observations complètes tirées du train, `seed=42`, déterministe.
- **Échantillon expliqué** : 25, 50 ou 100 lignes (défaut 50) tirées de la validation 2024, `seed=42`, sans valeurs manquantes.
- **Latences mesurées** (50 lignes, fond de 20, premier appel, puis caché) : Random Forest 0,5 s · GaussianNB 2,7 s · SVM 8,7 s · HGB/Zero-R/LR < 1 s. `st.cache_resource` et `st.cache_data` évitent tout recalcul.

HistGradientBoosting est un estimateur brut sans `.steps` et produit des log-odds : le `TreeExplainer` y est écarté (additivity non respectée au niveau probabilité), la permutation sur `predict_proba` fait foi. La régression logistique utilise la même échelle de probabilité que les autres modèles pour rester comparable.

### Page « Explicabilité » (`src/ui/shap_page.py`)

- **Beeswarm** : dispersion et signe des contributions par variable sur l'échantillon expliqué.
- **Barre** : importance moyenne (valeur absolue) par variable — les indices FWI/ISI/DC et les variables météo du jour y apparaissent en tête.
- **Waterfall individuel** : explique la dernière observation soumise au Prediction Studio. La légende affiche `base + contributions = score`, valeur contrôlée par les tests.
- Captions de prudence : lecture descriptive, pas causale ; variables corrélées qui partagent le signal.

### Interprétation scientifique

- **FWI, ISI, DC, DMC, BUI** sont des indices de feu construits à partir des mêmes variables météo (température, humidité, vent, précipitations) : quand l'humidité (`rh_min`, `rh_mean`) pousse le score vers 0 et que `temp_max` ou `fwi` le pousse vers 1, les contributions se répartissent entre la variable brute et l'indice qui la résume. Une part de signal est donc partagée par corrélations fortes, pas « distribuée » par le modèle de façon unique.
- **Sens physique cohérent** : humidité élevée → contribution négative ; sécheresse, chaleur, `vpd_max`, `ffmc`/`isi` élevés → contribution positive vers la classe « avec détection ».
- **Pourquoi ce n'est pas causal** : les observations sont rétrospectives et appariées (jours sans détection du même mois), les prédicteurs sont corrélés entre eux, et la météo de la journée observée est incluse. SHAP décrit *comment le modèle produit sa décision sur ces données*, il ne démontre pas que modifier la variable changerait le nombre d'incendies.
- **Limitation météo du jour** : la classification porte sur le jour étiqueté, pas sur une prévision à J+1. Le score ne préjuge pas du risque territorial futur.

## Mission C — Tests et vérifications

```bash
python -m pytest -q        # 169 tests, dont 60 ajoutés par IASD17
```

| Fichier | Contenu |
|---|---|
| `tests/test_alert_levels.py` | seuils du protocole, frontières exactes (0,199 / 0,2 / 0,349 / 0,35 / 0,499 / 0,5), scores invalides, badge |
| `tests/test_prediction_enhanced.py` | schéma CSV (ordre, colonnes manquantes, non numérique, infini, incohérence, `doy`), prédiction en lot fidèle à `predict_proba`, aller-retour CSV, badge en interface |
| `tests/test_shap_backend.py` | déterminisme du fond, stratégie par modèle, addativité des huit pipelines, non-réentraînement, rendu de la page et du waterfall sous `AppTest` |

L'upload de fichier n'est pas exposé par `AppTest` (streamlit 1.51) : le flux complet CSV → `validate_batch` → `predict_batch` → export est testé en unitaire sur les mêmes fonctions que l'interface.

## Démonstration (5 minutes)

1. **Prédiction mono** : Prediction Studio → pipeline par défaut (GaussianNB) → « Prédire » → lire classe, jauge, badge d'alerte et position sur les seuils.
2. **CSV de 10 lignes** : studio avancé → « Télécharger le modèle de colonnes » → préparer un fichier de 10 lignes (par exemple `training().dropna().head(10)` exporté) → charger → vérifier les quatre métriques d'alerte → « Télécharger les prédictions ».
3. **Waterfall** : revenir sur la page Explicabilité → la dernière observation soumise y est décomposée, `base + contributions = score`.
4. **Beeswarm et barre** : changer de pipeline (Random Forest : rendu quasi instantané) et constater l'importance des indices de feu et de l'humidité.

## Questions de soutenance

- **Pourquoi 24 features et pas 25 ?** Le protocole actif (`config/protocole.json`) fixe 24 variables sans métadonnée géographique ou temporelle ; `ndvi_normal` n'existe que dans les artefacts secondaires sklearn 1.9.0 (hors environnement et hors schéma).
- **Pourquoi SVM à 0,20 ?** Décision gelée sur la validation 2024 (F1 parmi trois seuils), publiée telle quelle sur le test 2025 (`results/test_final/result.json`).
- **Pourquoi SHAP n'est pas causal ?** Corrélations entre prédicteurs, échantillon apparié rétrospectif, météo du jour incluse : SHAP décompose la décision du modèle, pas l'effet physique d'une variable.
- **Limitation principale ?** La météo de la journée observée est un prédicteur de l'étiquette du même jour : le modèle reconstruit le jour étiqueté, il ne prédit pas l'avenir.

## Fichiers créés ou modifiés

**Créés :** `src/explainability/{__init__,alert_levels,shap_backend}.py`, `src/ui/{prediction_enhanced,shap_page}.py`, `tests/test_{alert_levels,prediction_enhanced,shap_backend}.py`, `docs/CONTRIBUTION_IASD17.md`, `docs/AUDIT_IASD17_PLAN.md`.

**Modifiés (minimalement) :** `src/ui/model_pages.py` (badge + section studio avancé), `src/ui/shell.py` et `src/app.py` (page Explicabilité), `requirements.txt` (+ `shap==0.54.1`), `docs/INTERFACE.md`, `README.md`.
