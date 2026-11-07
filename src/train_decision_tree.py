"""Train and evaluate a decision tree using the team's proposed temporal protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/processed/dataset_clean.csv"
DEFAULT_PROTOCOL = ROOT / "results/protocole_propose.json"

SCORING = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
    "roc_auc": "roc_auc",
    "average_precision": "average_precision",
}

PARAM_GRID = {
    "model__criterion": ["gini", "entropy"],
    "model__max_depth": [4, 8, 12, None],
    "model__min_samples_leaf": [5, 20, 50],
    "model__class_weight": [None, "balanced"],
}


def load_protocol(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as protocol_file:
        protocol = json.load(protocol_file)

    required_keys = {
        "statut",
        "train",
        "validation",
        "test_reserve",
        "cv_annees_validation",
        "metrique_principale",
        "features",
    }
    missing_keys = required_keys.difference(protocol)
    if missing_keys:
        raise ValueError(f"Protocole incomplet; clés absentes : {sorted(missing_keys)}")
    if protocol["metrique_principale"] != "f1_classe_1":
        raise ValueError(
            "La métrique principale du protocole doit être le F1 de la classe 1."
        )
    if not isinstance(protocol["features"], list) or not protocol["features"]:
        raise ValueError("Le protocole doit fournir une liste non vide de variables.")

    forbidden_features = {
        "label",
        "split",
        "sample_kind",
        "n_detections",
        "max_frp",
    }
    forbidden = forbidden_features.intersection(protocol["features"])
    if forbidden:
        raise ValueError(f"Variables interdites dans le modèle : {sorted(forbidden)}")
    return protocol


def build_temporal_splits(
    train: pd.DataFrame,
    cv_validation_years: list[int],
) -> list[tuple[np.ndarray, np.ndarray]]:
    splits = []
    for year in cv_validation_years:
        fit_indices = np.flatnonzero(train["year"].lt(year).to_numpy())
        validation_indices = np.flatnonzero(train["year"].eq(year).to_numpy())
        if not len(fit_indices) or not len(validation_indices):
            raise ValueError(f"Le pli de {year} n'a pas de données d'entraînement/validation.")

        fit = train.iloc[fit_indices]
        fold_validation = train.iloc[validation_indices]
        if fit["date"].max() >= fold_validation["date"].min():
            raise ValueError(f"Le pli de {year} ne respecte pas l'ordre temporel.")
        if fit["label"].nunique() != 2 or fold_validation["label"].nunique() != 2:
            raise ValueError(f"Le pli de {year} doit contenir les deux classes.")
        splits.append((fit_indices, validation_indices))
    return splits


def validate_partitions(df: pd.DataFrame, protocol: dict[str, Any]) -> None:
    required_columns = {
        "date",
        "year",
        "label",
        "split",
        *protocol["features"],
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Colonnes absentes du dataset : {sorted(missing_columns)}")

    train_start, train_end = (int(value) for value in protocol["train"].split("-"))
    expected_train_years = set(range(train_start, train_end + 1))
    actual_train_years = set(df.loc[df["split"].eq("train"), "year"].astype(int))
    if actual_train_years != expected_train_years:
        raise ValueError(
            "Les années train du dataset ne correspondent pas au protocole : "
            f"attendu {sorted(expected_train_years)}, obtenu {sorted(actual_train_years)}."
        )

    for split_name, protocol_key in (("val", "validation"), ("test", "test_reserve")):
        expected_year = int(protocol[protocol_key])
        actual_years = set(df.loc[df["split"].eq(split_name), "year"].astype(int))
        if actual_years != {expected_year}:
            raise ValueError(
                f"La partition {split_name} doit contenir uniquement {expected_year}; "
                f"années trouvées : {sorted(actual_years)}."
            )

    if set(df["split"].dropna().unique()) != {"train", "val", "test"}:
        raise ValueError("Le dataset doit avoir exactement les partitions train, val et test.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Entraîne un arbre de décision avec les plis temporels communs."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    if protocol["statut"] != "confirme":
        print(
            "ATTENTION : protocole encore proposé; confirme les plis et la métrique avec Hani "
            "avant de présenter ces scores comme définitifs."
        )

    df = pd.read_csv(args.data, parse_dates=["date"])
    validate_partitions(df, protocol)
    features = protocol["features"]

    train = (
        df.loc[df["split"].eq("train")]
        .sort_values(["date", "cell_id"] if "cell_id" in df.columns else ["date"])
        .reset_index(drop=True)
    )
    validation = df.loc[df["split"].eq("val")].copy()
    X_train = train[features]
    y_train = train["label"].astype(int)
    X_validation = validation[features]
    y_validation = validation["label"].astype(int)

    if set(y_train.unique()) != {0, 1} or set(y_validation.unique()) != {0, 1}:
        raise ValueError("Les partitions train et val doivent contenir les classes 0 et 1.")

    cv_splits = build_temporal_splits(
        train,
        [int(year) for year in protocol["cv_annees_validation"]],
    )
    print(
        f"Entraînement : {len(train):,} lignes; validation {protocol['validation']} : "
        f"{len(validation):,} lignes; plis temporels : {len(cv_splits)}."
    )
    grid_size = (
        len(PARAM_GRID["model__criterion"])
        * len(PARAM_GRID["model__max_depth"])
        * len(PARAM_GRID["model__min_samples_leaf"])
        * len(PARAM_GRID["model__class_weight"])
    )
    print(f"Grille : {grid_size} configurations; sélection par F1 de la classe 1.")

    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DecisionTreeClassifier(random_state=42)),
        ]
    )
    search = GridSearchCV(
        pipeline,
        PARAM_GRID,
        scoring=SCORING,
        refit="f1",
        cv=cv_splits,
        n_jobs=1,
        return_train_score=True,
        error_score="raise",
    )
    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    print("Meilleurs paramètres :", search.best_params_)
    print("F1 moyen CV :", f"{search.best_score_:.4f}")

    predicted = best_model.predict(X_validation)
    positive_index = list(best_model.classes_).index(1)
    scores = best_model.predict_proba(X_validation)[:, positive_index]
    result: dict[str, Any] = {
        "model": "DecisionTree",
        "n_features": len(features),
        "validation": str(protocol["validation"]),
        "val2024_accuracy": accuracy_score(y_validation, predicted),
        "val2024_precision": precision_score(y_validation, predicted, zero_division=0),
        "val2024_recall": recall_score(y_validation, predicted, zero_division=0),
        "val2024_f1": f1_score(y_validation, predicted, zero_division=0),
        "val2024_roc_auc": roc_auc_score(y_validation, scores),
        "val2024_average_precision": average_precision_score(y_validation, scores),
    }
    for metric in SCORING:
        result[f"cv_{metric}_mean"] = float(
            search.cv_results_[f"mean_test_{metric}"][search.best_index_]
        )
        result[f"cv_{metric}_std"] = float(
            search.cv_results_[f"std_test_{metric}"][search.best_index_]
        )
    tn, fp, fn, tp = confusion_matrix(y_validation, predicted, labels=[0, 1]).ravel()
    result.update(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp))

    results_dir = ROOT / "results"
    models_dir = ROOT / "models"
    results_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    tuning = pd.DataFrame(search.cv_results_)
    tuning.to_csv(results_dir / "recherche_arbre_decision.csv", index=False)
    pd.DataFrame([result]).to_csv(
        results_dir / "resultats_arbre_decision_validation.csv",
        index=False,
    )

    model_path = models_dir / "arbre_decision_developpement.joblib"
    joblib.dump(best_model, model_path)
    reloaded = joblib.load(model_path)
    if not np.array_equal(
        reloaded.predict(X_validation.iloc[:50]),
        best_model.predict(X_validation.iloc[:50]),
    ):
        raise RuntimeError("Les prédictions changent après rechargement du modèle.")

    print(
        f"Validation {protocol['validation']} : "
        f"accuracy={result['val2024_accuracy']:.4f}, "
        f"précision={result['val2024_precision']:.4f}, "
        f"rappel={result['val2024_recall']:.4f}, "
        f"F1={result['val2024_f1']:.4f}, "
        f"ROC-AUC={result['val2024_roc_auc']:.4f}."
    )
    print(
        f"Confusion : TN={tn}, FP={fp}, FN={fn}, TP={tp}. "
        f"Modèle sauvé avec scikit-learn {sklearn.__version__} : {model_path}."
    )
    print("Aucun score n'a été calculé sur le test réservé.")


if __name__ == "__main__":
    main()
