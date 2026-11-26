# Revue d’intégration de Prediction Studio

Le code examiné est celui de la branche IASD17 à `56c9285` et du studio SIAD03 à `7379a84`. Les six commits de la branche IASD17 sont conservés par la fusion. IASD17 a apporté les tranches du score, leur répartition dans les lots et un parcours d’import/export. SIAD03 a apporté le lecteur CSV borné, les contrôles du formulaire et l’intégration des deux parcours.

| Constat dans la branche IASD17 | Décision d’intégration et preuve |
|---|---|
| Deux sélecteurs de pipeline dans le même espace permettaient de consulter un modèle et d’en appliquer un autre au lot. | Le modèle et son seuil sont sélectionnés avant le choix « Observation individuelle » ou « Fichier CSV ». Le test Streamlit compte un sélecteur dans le mode lot. |
| Le badge utilisait « Critique » dès 0,50. Les quatre libellés pouvaient être lus comme une échelle de danger. | Le badge et le tableau du lot indiquent l’intervalle numérique du score de classe 1. À score 0,35, la tranche est la même pour tous, alors que la classe vaut 1 au seuil 0,20 et 0 au seuil 0,50. Les seuils visuels sont lus dans le protocole. |
| `validate_batch` projetait le tableau sur les 24 variables mais `predict_batch` réexportait le fichier original, extras et éventuelles formules compris. Les anciennes colonnes de résultat étaient écrasées. | L’en-tête brut est lu avant pandas. Les colonnes dupliquées ou étrangères, y compris les métadonnées de fuite, font rejeter le lot. Un export d’un format connu peut être réimporté. Seules les 24 mesures sont extraites, converties et réordonnées avant inférence. Les identifiants de ligne et résultats sont régénérés. |
| Le CSV IASD17 imposait l’ordre des colonnes et utilisait directement `pd.read_csv(upload)`, avec des limites différentes de celles du studio SIAD03. | L’ordre des colonnes est libre. Limites communes de 1 Mio et 1 000 lignes, UTF-8 avec ou sans BOM. La cohérence physique, les plages du formulaire et les nombres de jours entiers sont contrôlés avant de classer le lot. |
| Les cellules vides étaient toujours autorisées côté IASD17, toujours refusées côté SIAD03. | Par défaut, chaque mesure est requise. L’utilisateur peut activer le traitement des valeurs manquantes du modèle. Une ligne entièrement vide est refusée dans les deux modes. Les tests comparent l’option au résultat natif de chacun des huit estimateurs enregistrés. |

## Rejouer la recette

Depuis la racine, dans l’environnement Python 3.12 du projet :

```bash
python -m pytest -q -W error::FutureWarning tests/test_prediction_batch.py tests/test_prediction_enhanced.py tests/test_alert_levels.py tests/test_ui_app.py tests/test_ui_quality.py
```

Les tests couvrent les fichiers vides, mal formés et trop grands, les en-têtes dupliqués, manquants, supplémentaires ou permutés, les fuites, les collisions partielles, les types, les infinis, les mesures incohérentes et la correspondance avec le formulaire. Ils injectent une formule dans les anciens résultats d’un export réimporté et vérifient que le nouveau score vient du pipeline.

L’import reconnaît les 24 mesures seules ainsi que les signatures complètes et exactes des exports IASD17, SIAD03 et intégré. Toute autre colonne supplémentaire interrompt le traitement. Le mode d’emploi du studio décrit la saisie, le choix du modèle et l’export. [Interface](INTERFACE.md)
