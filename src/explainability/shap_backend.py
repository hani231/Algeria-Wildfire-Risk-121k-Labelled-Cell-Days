"""Back-end SHAP : exact sur les arbres, permutation model-agnostic ailleurs.

Les explications sont additives : base + somme des contributions = score du
modèle pour la classe 1. Aucun réentraînement : seuls le préprocesseur
figé et l'estimateur sauvegardés sont appelés.
"""
import numpy as np
import pandas as pd
import shap

TREE_MODELS = ('DecisionTreeClassifier', 'RandomForestClassifier')


def sample_background(data, features, size=20, seed=42) -> pd.DataFrame:
    """Échantillon de fond déterministe sur les observations complètes."""
    complete = data[list(features)].dropna()
    if complete.empty:
        raise ValueError('Aucune observation complète pour l’échantillon de fond.')
    return complete.sample(n=min(size, len(complete)), random_state=seed)


def _final_estimator(model):
    return model.steps[-1][1] if hasattr(model, 'steps') else model


def _preprocessor(model):
    if hasattr(model, 'steps') and len(model.steps) > 1:
        return model[:-1]
    return None


class PipelineExplainer:
    """Explique la probabilité de la classe 1 d'un pipeline entraîné.

    Stratégie « arbre » : TreeExplainer exact sur l'estimateur final,
    lecture de la classe 1 uniquement. Stratégie « permutation » :
    permutation des features sur predict_proba[:, 1] avec
    max_evals = 2p + 1, pour les modèles sans arbre interprétable.
    """

    def __init__(self, model, background):
        self.features = list(model.feature_names_in_)
        self.model = model
        self.background_size = len(background)
        estimator = _final_estimator(model)
        if type(estimator).__name__ in TREE_MODELS:
            self.strategy = 'arbre'
            self._tree = shap.TreeExplainer(estimator)
            self._prep = _preprocessor(model)
        else:
            self.strategy = 'permutation'
            classes = list(model.classes_)

            def predict_proba_1(raw):
                frame = pd.DataFrame(raw, columns=self.features)
                return model.predict_proba(frame)[:, classes.index(1)]

            self._explainer = shap.Explainer(predict_proba_1, background[self.features])

    def __call__(self, frame) -> shap.Explanation:
        """Contributions additives pour chaque ligne de `frame`."""
        observed = frame[self.features]
        if self.strategy == 'arbre':
            transformed = (self._prep.transform(observed) if self._prep is not None
                           else observed.to_numpy(dtype=float))
            explanation = self._tree(transformed)
            values = np.asarray(explanation.values, dtype=float)
            base = np.asarray(explanation.base_values, dtype=float)
            if values.ndim == 3:
                values, base = values[:, :, 1], base[:, 1]
            return shap.Explanation(values=values, base_values=base,
                                    data=observed.to_numpy(dtype=float),
                                    feature_names=self.features)
        explanation = self._explainer(observed, max_evals=2 * len(self.features) + 1,
                                      silent=True)
        if getattr(explanation, 'feature_names', None) is None:
            explanation.feature_names = list(self.features)
        return explanation


def make_explainer(model, background) -> PipelineExplainer:
    """Construit l'explicateur adapté au pipeline, sans réentraînement."""
    return PipelineExplainer(model, background)
