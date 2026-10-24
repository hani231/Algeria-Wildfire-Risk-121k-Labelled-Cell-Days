## Lire les résultats obtenus sur 2024

| Modèle | Accuracy | Précision classe 1 | Rappel classe 1 | F1 classe 1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Zero-R | 92,37 % | 0 (convention) | 0 % | 0 | 0,500 |
| GaussianNB | 48,11 % | 10,05 % | 72,94 % | 0,177 | 0,630 |

Zero-R obtient beaucoup de réponses correctes en choisissant toujours 0, mais rate les **643** exemples
positifs de validation. GaussianNB en retrouve **469**, en rate **174** et produit **4 197 faux positifs**.
La majorité de ses alertes ne correspond donc pas à une détection étiquetée.

Son F1 moyen sur les cinq plis vaut environ **0,410**, avec un écart-type de **0,130**, contre **0,177**
sur 2024. Cela montre une performance moins bonne sur cette année. Les changements entre années,
le déséquilibre des classes, les distributions et les hypothèses approximatives de GaussianNB
sont des pistes d’analyse ; ces scores ne permettent pas d’en attribuer la cause avec certitude.
Ce résultat de développement reste à comparer aux quatre autres modèles avec un protocole commun.
On ne modifie pas le test final 2025 pour masquer cette difficulté.
