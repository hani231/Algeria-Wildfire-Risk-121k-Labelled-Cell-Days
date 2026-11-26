"""Attributions du score de classe 1 par rapport à un même fond empirique."""
import numpy as np
import pandas as pd
import shap

TREE_MODELS = ('DecisionTreeClassifier', 'RandomForestClassifier')


def sample_background(data, features, size=20, seed=42) -> pd.DataFrame:
    """Tirer un fond parmi les observations complètes du train 2012–2023."""
    if not {'split', 'year'} <= set(data) or not (
            data.split.eq('train') & data.year.between(2012, 2023)).all():
        raise ValueError('Le fond requiert exclusivement des lignes du train 2012–2023.')
    complete = data[list(features)].dropna()
    if complete.empty:
        raise ValueError('Aucune observation complète pour l’échantillon de fond.')
    return complete.sample(n=min(size, len(complete)), random_state=seed)


class PipelineExplainer:
    """Décomposer le score du modèle sauvegardé, sans ajuster ses paramètres."""

    def __init__(self, model, background, seed=42):
        self.features = list(model.feature_names_in_)
        self.model = model
        self.positive = list(model.classes_).index(1)
        if list(background.columns) != self.features or background.empty:
            raise ValueError('Schéma du fond incompatible avec les entrées du modèle.')
        self.background = background.to_numpy(dtype=float)
        self.background_size = len(background)
        self.base = model.predict_proba(background)[:, self.positive].mean()
        estimator = model.steps[-1][1] if hasattr(model, 'steps') else model
        self.strategy = 'arbre' if type(estimator).__name__ in TREE_MODELS else 'permutation'
        if self.strategy == 'arbre':
            self.prep = model[:-1] if hasattr(model, 'steps') and len(model.steps) > 1 else None
            transformed = self.prep.transform(background) if self.prep is not None else self.background
            # Les deux pipelines arbres conservent l'ordre et la dimension des colonnes.
            self.tree = shap.TreeExplainer(estimator, data=transformed, model_output='probability',
                                           feature_perturbation='interventional')
        else:
            # Deux ordres et leurs inverses, communs à toutes les observations.
            # Le générateur local rend un résultat indépendant des requêtes Streamlit concurrentes.
            rng = np.random.default_rng(seed)
            self.orders = []
            for _ in range(2):
                order = rng.permutation(len(self.features))
                self.orders.extend([order, order[::-1]])

    def _permutation_values(self, row):
        """Estimer les valeurs de Shapley par différences marginales sur quatre chemins."""
        count = len(self.features)
        contributions = np.zeros(count)
        for order in self.orders:
            # Étape k : les k premières variables de l'ordre prennent leur valeur observée.
            # Les autres restent celles de chaque cellule-jour du fond, conservées ensemble.
            in_coalition = np.argsort(order) < np.arange(1, count + 1)[:, None]
            hybrids = np.where(in_coalition[:, None, :], row, self.background)
            frame = pd.DataFrame(hybrids.reshape(-1, count), columns=self.features)
            scores = self.model.predict_proba(frame)[:, self.positive]
            means = scores.reshape(count, self.background_size).mean(axis=1)
            contributions[order] += np.diff(means, prepend=self.base)
        return contributions / len(self.orders)

    def __call__(self, frame) -> shap.Explanation:
        if list(frame.columns) != self.features or frame.empty:
            raise ValueError('Les colonnes expliquées doivent suivre le schéma ordonné du modèle.')
        raw = frame.to_numpy(dtype=float)
        if self.strategy == 'arbre':
            transformed = self.prep.transform(frame) if self.prep is not None else raw
            explanation = self.tree(transformed)
            values = explanation.values[:, :, self.positive]
            bases = explanation.base_values[:, self.positive]
        else:
            values = np.stack([self._permutation_values(row) for row in raw])
            bases = np.full(len(frame), self.base)
        return shap.Explanation(values=values, base_values=bases, data=raw,
                                feature_names=self.features)


def make_explainer(model, background, seed=42) -> PipelineExplainer:
    """Construire un explicateur conditionné au modèle et au fond fournis."""
    return PipelineExplainer(model, background, seed)
