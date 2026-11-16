# SIAD03 : rendre les expériences Zero-R/NB reproductibles et vérifier la grille

L'entraînement Zero-R/NB n'était disponible que dans un notebook qui réécrit des fichiers
partagés. Le meilleur `var_smoothing` se trouvait à la borne supérieure de la grille.
Ce lot ajoute une commande autonome, étend la grille à 14 réglages sur les cinq plis
chronologiques existants et conserve modèles, résultats, empreintes et diagnostics.

Tous les fichiers présents à la base ebd4bf4 restent identiques. Ajouts uniquement dans
src/siad03_nb, tests/siad03_nb, results/siad03_nb et docs/siad03_nb.

Validation : 69 tests réussis, cinq avertissements de dépréciation Seaborn ; deux
exécutions indépendantes identiques hors durées. Aucun score sur 2025.

Le réglage choisi sur train vaut 1.0. Son F1 2024 (0.173585) est légèrement inférieur
au résultat historique (~0.1767) : ce lot améliore la reproductibilité sans promettre
un gain prédictif. Les anciens artefacts sont conservés. Protocole toujours proposé.

L'audit utilise le site du cours et son dépôt modèle ; la page de suivi des projets
notés est bloquée par le proxy réseau. Les documents signalent cette limite et les
responsabilités collectives restantes. Fusion uniquement après relecture de l'équipe.
