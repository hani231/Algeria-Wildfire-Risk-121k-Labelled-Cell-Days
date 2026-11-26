# RAPPORT D'AUDIT — PROJ-IASD12 Wildfire Atlas

> Document historique de la branche IASD17 au commit 56c9285. Les tests et libellés ci-dessous décrivent cette livraison. Les revues d’intégration détaillent le comportement livré pour la réévaluation. [Explications SHAP](REVUE_SHAP.md) · [Studio et CSV](REVUE_STUDIO.md)
### Phase 1 : analyse exclusive (aucune modification effectuée)
**Auteur :** IASD17 · **Date :** 24 novembre 2026 · **Cible de travail :** `~/projects/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days` (clone Git, branche `main`)

---

## 1. Résumé exécutif

Le dépôt est un **projet universitaire abouti et gelé** : benchmark de 6 classifieurs obligatoires + 2 supplémentaires, application Streamlit à 6 espaces, 61 fonctions de test, CI GitHub Actions, rapport PDF. Note d'équipe : **13,2/20**.

**Constat clé pour IASD17 :**

| Élément | État |
|---|---|
| Mission A (Streamlit) | **~70 % déjà fait** (prédiction mono-observation, validation, probabilité, seuil gelé 0,20). Manque : import CSV, export prédictions, niveaux d'alerte. |
| Mission B (SHAP) | **0 %** — absent du code, des requirements et des tests. Seule une permutation intra-mois existe (`src/siad03_extensions/explain.py`). |
| Mission C (tests/docs) | **~80 % existant** (109 tests annoncés, docs complètes). À étendre aux nouvelles fonctionnalités + fiche contribution. |
| Modèle `knn_pca_95.joblib` | **Non intégrable en l'état** : sklearn 1.9.0 (env cible 1.8.0), 4 objets séparés (pas un Pipeline), 25 features (dont `ndvi_normal`) ≠ schéma officiel 24 features. |
| Environnement local (copie d'audit) | **Non opérationnel** : Python 3.14 système, pas de venv, pas de sklearn/streamlit/shap installés. |
| Git | La copie d'audit initiale n'avait pas de `.git` ; le clone de travail `~/projects/...` a un historique complet (HEAD `da93591`). |

**Recommandation prioritaire (voir §13) :** étendre le Prediction Studio (CSV + alertes) → ajouter SHAP sur les pipelines du benchmark → tests + documentation + commits Git isolés.

---

## 2. Architecture actuelle (arbre)

```
Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/
├── README.md                    # Lancement, protocole, résultats, contributions
├── requirements.txt             # pandas 2.2.3, sklearn 1.8.0, streamlit 1.51… (PAS shap)
├── requirements-dev.txt         # + pytest 8.4.2, nbformat, nbclient, ipykernel
├── .github/workflows/tests.yml  # CI : Python 3.12, pip install, pytest -q
├── .streamlit/config.toml       # Thème sombre
├── config/protocole.json        # Contrat actif : 24 features, seuils, seed 42, sha256 brut
├── Dataset/
│   ├── dataset.csv              # BRUT unique — 121 869 × 37 (sha256 vérifié)
│   └── processed.csv            # Export historique (non utilisé par le benchmark)
├── data/
│   ├── raw/README.md            # Pointe vers Dataset/
│   └── processed/dataset_clean.csv
├── models/                      # Artefacts SECONDAIRES (non chargés par l'app)
│   ├── knn_pca_95.joblib        # KNN seul, sklearn 1.9.0, 22 Mo, 2001 voisins
│   ├── pca_95.joblib            # PCA n_components=0.95, 1.9.0
│   ├── imputer.joblib           # SimpleImputer median, 25 features (feature_names_in_)
│   ├── scaler.joblib            # StandardScaler, 1.9.0
│   ├── naive_bayes_developpement.joblib    # Pipeline, 1.8.0
│   ├── arbre_decision_developpement.joblib # Pipeline, 1.9.1 ⚠
│   └── zeror_developpement.joblib
├── src/
│   ├── app.py                   # Entrée Streamlit (6 pages)
│   ├── ui/
│   │   ├── shell.py             # Navigation latérale + en-têtes
│   │   ├── services.py          # Chargement pipelines, classify(), cache
│   │   ├── model_pages.py       # Modèles + Prediction Studio
│   │   ├── pages.py             # Accueil, Exploration, Méthodologie
│   │   ├── geography.py, curves.py, units.py, atlas.css, maghreb.geojson
│   ├── models.py                # Benchmark 6 modèles (GridSearchCV chronologique)
│   ├── preprocessing.py         # Lecture protocole + empreinte
│   ├── cleaning_guide.py        # clean_data() déterministe
│   ├── data_quality.py          # coherence_counts() — bornes physiques
│   ├── final_evaluation.py      # Évaluation 2025 gelée
│   ├── kfold_diagnostic.py, learning_curves.py, parameter_sensitivity.py…
│   ├── siad03_nb/               # Lot Zero-R/NB (contract, experiment)
│   └── siad03_extensions/       # benchmark 2 modèles +, EDA, explain (permutation)
├── notebooks/                   # 01 EDA, 02/03, 03_zeror_nb, 04_knn, acp
├── results/
│   ├── benchmark_final/         # ★ 6 pipelines + metrics + decision.json (SVM@0.20)
│   ├── siad03_extensions/benchmark/  # + LogisticRegression, HistGradientBoosting
│   ├── test_final/result.json   # Évaluation 2025 publiée
│   └── post_freeze/             # KFold, learning curves, sensibilité
├── tests/                       # 61 def test_ (109 tests annoncés) + sous-lots
├── docs/                        # Rapport PDF, INTERFACE, dictionnaire, audits…
└── figures/
```

---

## 3. Inventaire des composants existants

### 3.1 Données
- **121 869 lignes × 37 colonnes**, 1 423 cellules ; splits : train 2012–2023 (104 979), val 2024 (8 423), test 2025 (8 467).
- Nettoyage : `clean_data()` — doublons exacts retirés, cohérence date/year/doy, split temporel vérifié, colonnes de fuite (`sample_kind`, `n_detections`, `max_frp`) **supprimées**, NaN **conservés** (imputation dans le pipeline).
- Contrôle entrées utilisateur : `coherence_counts()` (bornes RH/NDVI/vent, ordre temp_min≤mean≤max, etc.).

### 3.2 Protocole (24 features officielles, ordre exact)
```
temp_max, temp_min, temp_mean, rh_min, rh_mean, wind_max, wind_mean,
precip_sum, vpd_max, precip_7d, precip_30d, days_since_rain_1mm,
temp_max_7d_mean, rh_min_7d_mean, ffmc, dmc, dc, isi, bui, fwi,
ndvi, ndvi_change_32d, ndvi_stale_days, doy
```
Interdits : `label, split, sample_kind, n_detections, max_frp, days_since_last_fire, ndvi_normal, ndvi_anomaly, year, cell_id, date, lat, lon`.

### 3.3 Modèles chargés par l'application (`src/ui/services.py`)

| Modèle | Fichier | Type | sklearn | Features |
|---|---|---|---|---|
| Zero-R, GaussianNB, DecisionTree, Random Forest, K-NN, SVM | `results/benchmark_final/*.joblib` | **Pipeline** (imputer [± scaler] + classifieur) | **1.8.0** | 24, `feature_names_in_` présent ✓ |
| LogisticRegression, HistGradientBoosting | `results/siad03_extensions/benchmark/*.joblib` | Pipeline/estimateur | 1.8.0 | 24 ✓ |

- **Décision gelée** : SVM @ seuil **0,20** (`decision.json`, commit `ece0598`). Test 2025 : F1 0,263, rappel 0,802, ROC-AUC 0,610, AP 0,178.
- Tous ont `predict_proba` (SVM `probability=True` → score de Platt).
- Validation du chargement : `InconsistentVersionWarning` → erreur + vérification schéma/ classes {0,1}.

### 3.4 Artefacts secondaires `models/` (non intégrés)
- `knn_pca_95` + `pca_95` + `imputer` + `scaler` : **sklearn 1.9.0**, **25 features** avec `ndvi_normal` et `doy` en tête, **4 objets séparés** (pas de `Pipeline`, le KNN n'a pas de `feature_names_in_`). AP 2024 = 0,1052. Incompatible avec l'env 1.8.0 et le protocole 24 features.
- `arbre_decision_developpement.joblib` : sklearn **1.9.1** ⚠.
- `naive_bayes_developpement` : 1.8.0 (pipeline OK).

### 3.5 Interface existante
6 espaces : Accueil, Exploration (EDA + export sélection CSV), Carte, Modèles (classement + matrices + courbes), **Prédiction**, Méthodologie.
Le Prediction Studio (`model_pages.py:119`) offre déjà : choix du pipeline, 24 number_inputs groupés avec min/max issus du train, validation d'incohérences, bouton Prédire, classe binaire, **probabilité**, seuil 0,20 si SVM, persistance en `st.session_state`.

### 3.6 Tests & docs
- 61 fonctions de test (AppTest Streamlit, artefacts, contrat, EDA, statistiques, KFold…), CI Python 3.12.
- Docs : rapport PDF/MD, INTERFACE.md, dictionnaire, SOURCES, audits, matrice de conformité.

### 3.7 Explicabilité actuelle
- **Pas de SHAP.** Permutation intra-mois sur 2 modèles (`explain.py`) + coefficients de régression logistique affichés en barre dans Model Arena.
- `docs/siad03_extensions/RAPPORT.md` : SHAP explicitement **écarté** comme « extension future ».

---

## 4. État des modèles et points techniques critiques

| # | Point | Détail |
|---|---|---|
| 1 | **Entrées des modèles** | DataFrame 24 colonnes, ordre exact du protocole, float. `classify()` reconstruit le frame dans `feature_names_in_`. |
| 2 | **Préprocessing** | Sauvegardé **dans chaque Pipeline** (SimpleImputer median ± StandardScaler). Les objets `models/imputer\|scaler\|pca` ne servent qu'au lot secondaire. |
| 3 | **Cohérence train/inférence** | Même `clean_data`, même protocole, empreinte SHA-256 du brut vérifiée. Pas de fuite dans le benchmark (fuites démontrées exclues). |
| 4 | **Fuite résiduelle discutée** | `ndvi_normal` dans les 25 features secondaires (normale 2000–2011, provenance à confirmer). Météo du jour → classification **rétrospective** (limitation documentée). |
| 5 | **Compatibilité** | Benchmark = 1.8.0 = version pinée. `knn_pca_95` = 1.9.0 → `InconsistentVersionWarning` bloquant dans `services._load_pipeline`. |
| 6 | **SHAP faisable ?** | **Oui sur les 8 pipelines du benchmark** (voir §5, Mission B). **Non directement** sur `knn_pca_95` sans reconstruction manuelle imputer→scaler→pca→knn sous 1.9.0. |
| 7 | **Méthode de prédiction correcte** | `pipeline.predict_proba(X_24_cols)[0, idx_classe_1]` puis `score >= seuil` (0,20 SVM / 0,50 sinon). Ne jamais appeler le KNN-PCA seul. |
| 8 | **Double protocole** | `config/protocole.json` (actif) vs `results/protocole_propose.json` (historique) — mêmes 24 features, statuts différents. |
| 9 | **Environnement local** | Python 3.14 système, **aucune dépendance installée** dans la copie d'audit → impossible de lancer tests/app en l'état. Python 3.12 exigé. |
| 10 | **Git** | Copie d'audit sans `.git` ; clone de travail `~/projects/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days` disponible avec historique (`da93591`, suivi `origin/main`). |

---

## 5. Missions IASD17 — faisabilité

### Mission A — Application Streamlit (compléments)

| Fonctionnalité | État | Travail restant |
|---|---|---|
| Saisie interactive 24 variables | ✅ Existant | — |
| Validation entrées | ✅ `coherence_counts` + entiers + bornes | — |
| Prédiction + probabilité | ✅ Existant | — |
| Seuil / lecture alerte binaire | ✅ Classe 0/1 | — |
| **Niveau d'alerte multi-cibles** | ❌ | Nouveau : mapping score → 4 niveaux (ex. <0,20 Faible / <0,35 Modéré / <0,50 Élevé / ≥0,50 Critique) aligné sur les seuils du protocole |
| **Import CSV batch** | ❌ (aucun `file_uploader` dans le projet) | Nouveau : upload, contrôle schéma/colonnes, prédiction en lot |
| **Export prédictions** | ❌ côté prédiction (seul l'EDA a un download) | Nouveau : `st.download_button` CSV |

**Faisabilité : haute.** Réutiliser `pipeline()`, `classify()`, `coherence_counts()`.

### Mission B — SHAP

| Élément | Faisabilité |
|---|---|
| Explainer compatible | **`shap.Explainer(model.predict_proba, background)`** (model-agnostic) pour tous ; **`shap.TreeExplainer`** pour Random Forest / DecisionTree / HistGradientBoosting (rapide, exact) ; **`shap.LinearExplainer`** pour LogisticRegression. K-NN, GaussianNB, SVM → KernelExplainer/PermutationExplainer sur **échantillon** (50–100 fonds). |
| Background | Échantillon du train via `training()` (déjà caché Streamlit), grain 42. |
| Summary/Beeswarm + Bar | `shap.summary_plot(..., plot_type="beeswarm")` / `"bar"` sur échantillon val 2024 (max ~1 000 lignes pour la latence). |
| Explication individuelle | Waterfall/force plot sur la ligne soumise dans Prediction Studio. |
| Dépendance à ajouter | `shap` dans `requirements.txt` (pin compatible numpy 2.3.5 / sklearn 1.8.0 — vérifier `shap>=0.46`). |
| **Non recommandé** | SHAP sur `knn_pca_95` (env 1.9.0, schéma 25, hors protocole). |

**Faisabilité : moyenne** (intégration UI + latence à maîtriser par cache `st.cache_resource`).

### Mission C — Tests & documentation

- Patterns existants : `AppTest`, fixtures `conftest.py`, tests artefacts/contrat.
- À ajouter : tests import CSV, export, niveaux d'alerte, explainer SHAP (smoke test sur 1 modèle léger type GaussianNB), validation schéma CSV invalide.
- Docs : étendre `docs/INTERFACE.md`, nouvelle `docs/CONTRIBUTION_IASD17.md`, README (section contributions).

---

## 6. Problèmes techniques identifiés

1. **Copie d'audit sans `.git`** → cloner (fait : `~/projects/...`) avant toute contribution.
2. **Environnement non installé** (Python 3.14, pas de venv, pas de sklearn) → rien ne s'exécute dans la copie d'audit.
3. **SHAP absent** (requirements + code + tests).
4. **`knn_pca_95` non intégrable** : version 1.9.0, 4 objets désassemblés, schéma 25 ≠ 24, `ndvi_normal` hors protocole.
5. **`arbre_decision_developpement.joblib` en 1.9.1** (incompatible 1.8.0 s'il était chargé).
6. **Pas d'import/export CSV** dans le studio de prédiction.
7. **Pas de niveau d'alerte** au-delà du binaire.
8. **Latence potentielle SHAP** sur SVM/KNN (kernel) → obligatoire : échantillonnage + cache.
9. **Deux protocoles JSON** coexistant (risque de confusion, mineur).
10. **Documentation contribution IASD17 absente** (les docs listent SIAD03 et deux rôles « à confirmer »).

---

## 7. Fonctionnalités manquantes (vs attentes prof)

- Application interactive Streamlit : **partiellement** (compléments A).
- Prédiction risque : **oui** (rétrospective, à expliciter).
- Explicabilité SHAP : **non**.
- Analyse importance variables météo/FWI : **partielle** (permutation + coefs logreg) → à compléter par SHAP.
- Tests & docs : **oui**, à étendre.
- Traçabilité Git individuelle : **à créer** sur branche dédiée.

---

## 8. Risques et dépendances

| Risque | Impact | Atténuation |
|---|---|---|
| Conflits sur fichiers partagés (`model_pages.py`, `services.py`) | Conflits d'équipe | Branches dédiées, ajout de modules neufs, édits minimaux |
| Python 3.12 absent du poste | Rien ne tourne | venv 3.12 + `requirements-dev.txt` (priorité jour 1) |
| shap incompatible numpy/sklearn | Échec install | Pin testé, CI |
| SHAP lent sur SVM | UI figée | Échantillon + `cache_resource` + limite de lignes |
| Réentraînement interdit | — | Aucun `fit` en production ; SHAP = inférence seule |
| Écarts `ndvi_normal`/25 features | Confusion schéma | Rester sur les 24 features du protocole pour toute nouvelle UI |

---

## 9. Architecture cible proposée

```
src/
├── app.py                          # inchangé (+ éventuelle page Explicabilité)
├── ui/
│   ├── model_pages.py              # MINIMAL : boutons onglets / renvoi vers nouveaux modules
│   ├── services.py                 # MINIMAL : réutiliser pipeline/classify (imports)
│   ├── prediction_enhanced.py       # ★ IASD17 : alerte multi-niveaux, import CSV, export
│   └── shap_page.py                # ★ IASD17 : summary, bar, waterfall individuelle
├── explainability/
│   ├── __init__.py
│   ├── shap_backend.py             # ★ fabrication Explainer + cache + calculs
│   └── alert_levels.py             # ★ mapping score → niveau d'alerte + libellés FR
tests/
├── test_prediction_enhanced.py      # ★ IASD17
├── test_alert_levels.py            # ★ IASD17
└── test_shap_backend.py            # ★ IASD17 (smoke)
docs/
├── CONTRIBUTION_IASD17.md          # ★ description contribution
└── INTERFACE.md                    # § Prédiction / Explicabilité mis à jour
requirements.txt                    # + shap (pin vérifié)
```

Principe : **ajouts modulaires**, zéro réécriture des fichiers des autres, réutilisation de `services.pipeline/classify/training`.

---

## 10. Plan de développement IASD17 (7 phases / 9 jours)

### Phase 1 — Compréhension & préparation (J1) — *priorité critique, facile*
| Tâche | Détail |
|---|---|
| Travailler depuis le clone `~/projects/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days` | **Validation** : `git log` affiche l'historique · **Résultat** : branche `feature/iasd17-studio-shap` créée |
| venv Python 3.12 + `pip install -r requirements-dev.txt` | **Validation** : `pytest -q` vert · **Résultat** : environnement exécutable |
| Relecture ciblée `services.py`, `model_pages.py`, `contract.py` | Lecture seule |

### Phase 2 — Architecture de l'app (J2) — *haute, moyenne*
| Tâche | Détail |
|---|---|
| Créer `src/ui/prediction_enhanced.py` (squelette + navigation) | **Fichiers** : `prediction_enhanced.py`, edit minimal `model_pages.py` ou `app.py` · **Dép.** : streamlit · **Validation** : page charge sans exception (`AppTest`) · **Résultat** : onglet/section « Studio avancé » |
| Créer `src/explainability/` (alertes d'abord) | **Fichiers** : `alert_levels.py` · **Validation** : seuils 0,20/0,35/0,50 du protocole respectés |

### Phase 3 — Fonctionnalités de prédiction (J3–J4) — *critique, moyenne*
| Tâche | Détail |
|---|---|
| Niveaux d'alerte (Faible/Modéré/Élevé/Critique) + badges colorés | **Fichiers** : `alert_levels.py`, `prediction_enhanced.py` · **Dép.** : units.py pour libellés · **Validation** : seuils = `protocole.thresholds` ; tests unitaires frontières · **Résultat** : gauge + libellé explicatif (score ≠ probabilité spatiale) |
| Import CSV (upload → contrôle schéma 24 colonnes → prédiction batch) | **Fichiers** : `prediction_enhanced.py`, `tests/test_prediction_enhanced.py` · **Dép.** : pandas · **Validation** : CSV valide → N lignes prédites ; colonne manquante/ordre invalide → message clair ; aucune écriture sur Dataset/ · **Résultat** : DataFrame colonnes `score, prediction, alerte` |
| Export prédictions CSV | **Validation** : `download_button` produit un CSV lisible par `read_csv` |

### Phase 4 — Intégration SHAP (J5–J6) — *haute, difficile*
| Tâche | Détail |
|---|---|
| Ajouter `shap` (pin compatible) | **Fichiers** : `requirements.txt` · **Validation** : CI verte |
| `shap_backend.py` : choix explainer par modèle + cache | **Fichiers** : `src/explainability/shap_backend.py` · **Dép.** : training() pour background (50–100 lignes, seed 42) · **Validation** : shapes (n, 24) ; aucun `fit` · **Résultat** : API `get_explainer(name) -> Explainer` |
| Page SHAP : Summary (beeswarm) + Bar (global) | **Fichiers** : `src/ui/shap_page.py` · **Validation** : 8 pipelines du benchmark chargent ; rendu < ~10 s sur échantillon · **Résultat** : importance globale FWI/météo visible |
| Waterfall individuel branché sur la prédiction du studio | **Validation** : explique la ligne soumise, cohérente avec `predict_proba` |
| Interprétation scientifique (texte) | **Fichiers** : `docs/CONTRIBUTION_IASD17.md` · **Contenu** : FWI/ISI/DC vs RH/temp, prudence causale, limitation rétrospective |

### Phase 5 — Tests & validation (J7) — *critique, facile-moyenne*
| Tâche | Détail |
|---|---|
| Tests unitaires : alertes, schéma CSV, shap_backend | **Fichiers** : `tests/test_alert_levels.py`, `tests/test_prediction_enhanced.py`, `tests/test_shap_backend.py` · **Validation** : `pytest -q` complet vert |
| Tests d'intégration AppTest : parcours upload → prédiction → export ; page SHAP sans exception | **Validation** : sans `app.error` |
| Recette manuelle (recette INTERFACE.md existante étendue) | 3 largeurs d'écran |

### Phase 6 — Documentation & Git (J8) — *haute, facile*
| Tâche | Détail |
|---|---|
| `docs/CONTRIBUTION_IASD17.md` + maj `INTERFACE.md` + § README | **Validation** : commandes de lancement reproductibles depuis un clone vierge |
| Commits atomiques sur branche dédiée | **Stratégie Git** (§11) |
| Pas de touch aux artefacts `models/`, `results/benchmark_final/`, `Dataset/` | **Validation** : `git status` propre hors fichiers IASD17 |

### Phase 7 — Démonstration (J9) — *moyenne, facile*
- Script de démo : 1 prédiction mono + 1 CSV 10 lignes + 1 waterfall SHAP + 1 beeswarm.
- Préparer les réponses : pourquoi 24 features et pas 25 ; pourquoi SVM@0,20 ; pourquoi SHAP n'est pas causal ; limitation météo du jour.

### Répartition chronologique synthétique

| Jour | Focus |
|---|---|
| J1 | Git + venv + pytest + relecture |
| J2 | Architecture modules neufs |
| J3 | Niveaux d'alerte + tests |
| J4 | Import CSV + export + tests |
| J5 | shap requirements + backend |
| J6 | Page SHAP (global + individuel) |
| J7 | Tests intégration + CI |
| J8 | Docs + commits + PR |
| J9 | Démo + répétition |

---

## 11. Fichiers concernés

**À créer :**
```
src/explainability/__init__.py
src/explainability/alert_levels.py
src/explainability/shap_backend.py
src/ui/prediction_enhanced.py
src/ui/shap_page.py
tests/test_alert_levels.py
tests/test_prediction_enhanced.py
tests/test_shap_backend.py
docs/CONTRIBUTION_IASD17.md
```

**À modifier (minimalement) :**
```
requirements.txt                      # + shap
src/app.py ou src/ui/model_pages.py   # enregistrer les nouvelles sections
docs/INTERFACE.md                     # sections Prédiction / Explicabilité
README.md                             # ligne contribution IASD17
```

**Interdits (ne pas toucher) :**
```
Dataset/**, models/*.joblib, results/benchmark_final/**, config/protocole.json,
src/cleaning_guide.py, src/models.py, src/preprocessing.py, travail SIAD03/siad03_*
```

---

## 12. Stratégie Git pour isoler les contributions IASD17

1. Travailler depuis `~/projects/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days` (clone avec historique, `main` suivi de `origin/main`, HEAD `da93591`).
2. Branche : `feature/iasd17-studio-shap` (une seule branche, couvrant A+B+C).
3. Commits atomiques et réguliers (conventional commits en français) :
   - `feat(iasd17): niveaux d'alerte multi-seuils dans le studio`
   - `feat(iasd17): import CSV et export des prédictions`
   - `feat(iasd17): backend SHAP model-agnostic avec cache`
   - `feat(iasd17): page SHAP summary/beeswarm/bar et waterfall individuelle`
   - `test(iasd17): alertes, import CSV et smoke SHAP`
   - `docs(iasd17): contribution, interface et README`
4. Ne jamais committer : `Dataset/`, `.venv/`, artefacts recréés, `results/` sauf sorties IASD17 si souhaitées dans `results/iasd17/`.
5. PR vers la branche principale avec checklist : CI verte, aucun fichier tiercier modifié, capture d'écran démo.

---

## 13. Recommandation finale — priorités IASD17

**Ordre d'implémentation recommandé :**

1. **🔴 Critique — Phase 1** : venv Python 3.12 + pytest vert sur le clone (sans rien d'autre ne peut démarrer).
2. **🔴 Critique — Mission A étendue** : niveaux d'alerte multi-seuils + **import CSV + export prédictions** dans le Prediction Studio. C'est le plus visible pour le professeur et 100 % réutilise l'existant.
3. **🟠 Haute — Mission B** : SHAP sur les **8 pipelines du benchmark** (pas `knn_pca_95`) : Beeswarm + Bar globaux, Waterfall individuel couplé à la prédiction, interprétation FWI/météo.
4. **🟠 Haute — Mission C** : tests des nouvelles fonctionnalités + `CONTRIBUTION_IASD17.md` + maj INTERFACE/README.
5. **🟡 Moyenne — Démonstration** : script de démo J9.
6. **⚪ Éviter** : réentraîner, intégrer `knn_pca_95` (incompatible), modifier le protocole ou le travail des autres.

**Points à confirmer avant Phase 2 :**
- Python 3.12 installable sur la machine (pyenv/uv) ?
- Validation de l'architecture cible (modules `explainability/` + `prediction_enhanced.py`, édit minimal de `model_pages.py`) ?
- Écart accepté : la copie d'audit sans `.git` vs le clone de travail dans `~/projects`.
