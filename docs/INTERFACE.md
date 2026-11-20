# Atlas des détections en Algérie

Depuis la racine, avec Python 3.12 :

    python -m pip install -r requirements-dev.txt
    python -m streamlit run src/app.py

Sur Windows, dans le venv du projet, remplacer python par .\.venv\Scripts\python.exe.
Le navigateur affiche l’adresse locale indiquée dans le terminal.

| Page | Utilisation |
|---|---|
| Accueil | Couverture du CSV, effectifs d’entraînement, résultats sur 2024 et raccourcis. |
| Exploration | Ajuster la plage météo, les années, classes, mois et zones ; réinitialiser dans la barre latérale. Ouvrir l’aperçu pour les types et l’évolution annuelle. |
| Statistiques | Comparer température et humidité avec ou sans appariement mensuel. Les courbes montrent les écarts annuels. |
| Modèles | Choisir une métrique, puis consulter la confusion et les réglages d’un modèle. |
| Prédiction | Modifier les mesures, puis cliquer sur Prédire. Le pipeline sauvegardé assure le prétraitement et le classement. |
| Méthodologie | Source, nettoyage, protocole temporel, contributions et limites. |

Conserver Dataset/dataset.csv, le protocole dans results/, les résultats d'audit dans
results/audit_siad03 et les lots results/siad03_nb/run_01 et results/siad03_extensions/benchmark.
Les deux modèles personnels utilisent le lot NB à 14 réglages. Les autres scores sont ceux du benchmark.
Les scores de l'arbre historique sont indicatifs (version scikit-learn différente).
Les tableaux utilisent la validation 2024 ; 2025 reste réservé. Les tuiles géographiques et
diagnostics avancés restent accessibles dans le dashboard scientifique autonome.

Captures de l’accueil : [ordinateur](interface-bureau.png) · [mobile](interface-mobile.png).
