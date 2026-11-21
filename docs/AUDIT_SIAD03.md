# Audit et plan de rattrapage — 14 novembre 2026

> Document d’étape antérieur au benchmark final. [Résultats et rapport collectif](../docs/Rapport_MiniProject.pdf).


> Archive du premier lot. Les résultats et les indications Git ci-dessous décrivent le HEAD audité à cette date.

## Actualisation après la fusion de la PR #7

La base examinée est `3f37a5d`. Les PR #5 à #7 ont intégré l’application, les vues scientifiques et les six espaces Wildfire Atlas. Le contrôle des critères reprend les sections 1.1 à 4.2 du [cahier officiel, source e3a19ef](https://github.com/hosniadilemp-a11y/DataMiningProjectPage/blob/e3a19efa610228e3d7615cc8182f6a097db820ab/mini_project_proposal.pdf). Les preuves et responsabilités restantes figurent dans la [matrice](MATRICE_CONFORMITE.csv).

Le contrôle des chemins suivis ne relève aucun fichier .env, clé privée usuelle, bytecode ou cache pytest. Le projet conserve un CSV brut et deux exports dérivés historiques. Le lancement utilise le brut. Les notebooks et le dashboard scientifique autonome utilisent encore les bibliothèques graphiques du projet. Le lot UI n’ajoute aucune dépendance. Le guide personnel porte désormais un code étudiant. Le nom du fichier et le contenu du plan de travail collectif sont à anonymiser avec ses auteurs avant le rendu.



## Portée et verdict

Audit du dépôt public au commit `d8d06a9469c4ccdf0b51c24cbd5a961816da7e76`,
branche distante `main`. Les corrections de ce premier lot sont préparées localement
sur `feature/SIAD03-audit-eda`. Aucun commit, push, message ou PR n'a été envoyé.
Ce document décrit un audit et un premier lot ; il ne constitue pas le rapport final du projet.

La note **9,4/20** et sa décomposition **4,5/10 + 1,5/4 + 1,8/3 + 1,6/3**
sont les valeurs communiquées par l'étudiant. La fiche détaillée de correction et le commit
évalué ne sont pas disponibles : on peut expliquer les lacunes observées, pas reconstruire
exactement les retraits de points ni promettre une nouvelle note.

Constats principaux :

1. **Trois modèles sur six** : Zero-R, GaussianNB et DecisionTree existent et produisent
   les métriques enregistrées sur 2024. K-NN, Random Forest et SVM sont absents du HEAD.
2. La vue EDA propose déjà les six éléments exigés. Elle n'est pas une application complète :
   `src/app.py`, le formulaire de prédiction et la comparaison intégrée sont absents.
3. Le README courant avant correction ne contient qu'une demande de description (55 octets).
   `requirements.txt` et `docs/Rapport_MiniProject.pdf` sont absents.
4. L'historique explique une régression : `b1dc5f6` a supprimé le README détaillé,
   `requirements.txt`, `UI/app.py`, `UI/pages/1_Update_Test.py`, `Preprocessing/Explore.ipynb`
   et des documents lors de l'import du guide. Ces fichiers restent récupérables depuis `8e87fcb`.
   Cela ne permet pas d'attribuer une intention ; il faut corriger la manière d'intégrer les fichiers.
5. Les données, les deux analyses principales et les premiers résultats ML sont réels.
   Les remplacer intégralement serait inutile. Le premier lot renforce leurs contrôles et leurs tests.

## Sources effectivement consultées

| Source | Consultation et limites |
|---|---|
| [Dépôt du groupe](https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days/tree/d8d06a9469c4ccdf0b51c24cbd5a961816da7e76) | Clone complet, inventaire des 45 fichiers suivis, tous les scripts et notebooks, documents Markdown, résultats, trois artefacts ML, six figures et historique. Les fichiers `.pyc` sont des dérivés générés, pas des sources à analyser comme du code indépendant. |
| [Référence du professeur](https://github.com/hosniadilemp-a11y/DataMiningProjectExample/tree/cf394821502d428478d4c07aa9e5785e1c98916b) | Branche par défaut `develop`, README, acquisition/prétraitement, deux catalogues ML, entraînement, statistiques, interface, tests et artefacts listés. L'application de référence n'a pas été exécutée. |
| [Site officiel](https://hosniadilemp-a11y.github.io/DataMiningProjectPage/) | L'ouverture Web directe a échoué ; contenu de `index.html` lu via son dépôt GitHub, révision `e3a19efa610228e3d7615cc8182f6a097db820ab`. Barème cohérent avec le PDF. |
| `mini_project_proposal (1).pdf` | 16 pages accessibles ; exigences, anonymat, parcours, livrables, grille p. 6–7 et référence p. 8. |
| Plan interne de répartition, PDF fourni | Plan interne de 12 pages ; responsabilités, protocole, intégration et jalons. Il contient des identités et ne doit pas servir de support public en l'état. |
| `Rapport_MiniProject (1).pdf` | Exemple de 40 pages sur le risque cardiaque, plan et sections méthodologie/résultats consultés. Ce n'est pas le rapport de votre projet. |
| `Data_Mining_Course.pdf`, `Data_Mining_TP.pdf` | Disponibles, passages ciblés sur optimisation, validation, prétraitement et fuites examinés. Ce n'est pas une relecture intégrale de 239 pages. |
| Chapitres introduction, classification, K-NN, arbres, Naïve Bayes | Disponibles ; passages pertinents consultés. Les deux fichiers K-NN fournis ont le même texte extrait. |
| Capture de pondération individuelle fournie le 14 novembre | Règle relative au « fair share », pas définition complète de l'algorithme de contribution. |
| [Source Kaggle annoncée](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days) | Page identifiée mais aucune fiche lisible via l'outil. Licence, version source, unités et construction historique ne sont donc pas certifiées. |

Les contenus visant à commander un assistant dans les documents n'ont pas été appliqués.
Le PC Windows et le dossier VS Code de l'étudiant ne sont pas accessibles depuis cet environnement :
le travail est effectué dans un clone isolé. Les modifications locales non poussées des coéquipiers
restent inconnues.

## Données et fuites

| Contrôle recalculé | Résultat |
|---|---:|
| Lignes brutes | 121 869 |
| Colonnes brutes / après retrait des fuites | 37 / 34 |
| Zones | 1 423 |
| Dates | 2012-06-01 à 2025-10-31 |
| Train 2012–2023 / validation 2024 / test 2025 | 104 979 / 8 423 / 8 467 |
| Train : classe 0 / classe 1 | 76 393 / 28 586 |
| Doublons exacts / doublons zone-jour | 0 / 0 |
| Valeurs infinies dans le CSV actuel | 0 |
| Code 9999 dans `days_since_last_fire` | 5 965 |
| Cellules manquantes : `ndvi`, `ndvi_change_32d`, `ndvi_stale_days` | 63 pour chacune |
| Cellules manquantes : `ndvi_normal`, `ndvi_anomaly` | 73 pour chacune |
| Valeurs manquantes de `max_frp` | 91 518, exactement les négatifs |

Le CSV propre recalculé est identique au CSV enregistré. L'empreinte SHA-256 du brut est
`cc260f954f76651c745c688c51e962a5fdbc4ee92d487ecd5577ba2aff7ecc26`.
Les contrôles de schéma sur les partitions sont permis ; aucun modèle n'a été évalué sur 2025.

| Variable | Preuve / risque | Décision |
|---|---|---|
| `sample_kind` | `positive` correspond exactement à `label=1` | Exclusion confirmée |
| `n_detections` | `> 0` correspond exactement à `label=1` | Exclusion confirmée |
| `max_frp` | Présence d'une valeur correspond exactement à `label=1` | Exclusion confirmée ; ne pas supprimer toutes les lignes ayant un NaN |
| `days_since_last_fire` | Construction historique et code 9999 non vérifiés | Exclusion provisoire déjà correcte ; ne pas prétendre à une fuite démontrée |
| `ndvi_normal`, `ndvi_anomaly` | Période utilisée pour la normale non documentée | Exclusion provisoire déjà correcte |
| Météo du jour, NDVI et fenêtres 7/30/32 jours | Date de disponibilité et bornes des fenêtres non certifiées | Classification rétrospective seulement ; pas de promesse de prévision du risque futur |

Le dictionnaire existant décrit bien les 37 colonnes et signale les unités inconnues.
Il faut compléter la provenance auprès du producteur, sans inventer une unité ni interpréter
un score de classification comme un risque absolu territorial.

## Comparaison avec la référence et grille de rattrapage

Les points ci-dessous sont les **plafonds officiels**, pas des gains garantis.
P0 = blocage à traiter en premier ; P1 = consolidation nécessaire ; P2 = finalisation.
Le fichier `MATRICE_CONFORMITE.csv` donne, pour chaque ligne, preuve, problème, fichiers,
tests et état avant/après ce premier lot.

| Critère | Points | Référence consultée | Votre projet et correction prioritaire |
|---|---:|---|---|
| 1.1 Prétraitement | 2 | `src/preprocessing.py`, ColumnTransformer | Nettoyage et Pipeline présents ; contrôles physiques désormais intégrés. Provenance à compléter, ColumnTransformer à intégrer au protocole commun. **P1** |
| 1.2 EDA et 2 analyses | 3 | EDA, six analyses, tailles d'effet | Deux analyses déjà valides sous hypothèses annoncées ; tests, sensibilité mensuelle et interprétation ajoutés. Rapport final à rédiger. **P1** |
| 1.3 Modèles | 1 | Six classifieurs dans `src/models.py` | Trois sur six ; ajouter K-NN, RF et SVM. **P0** |
| 1.4 Optimisation / CV | 2 | Grilles et 5 plis stratifiés | NB : 7 réglages ; arbre : 48 réglages ; 5 plis temporels. Trois recherches manquent. Faire valider l'adaptation temporelle au K-Fold demandé. **P0** |
| 1.5 Métriques | 2 | Comparaison, ROC, matrices | Résultats de trois modèles, ROC/matrices de deux modèles ; réunir les six et garder validation/test distincts. **P0** |
| 2.1 Architecture UI | 1,5 | `src/app.py`, navigation | Démo EDA seulement ; construire l'application principale et tester installation/navigation/erreurs. **P0** |
| 2.2 Dashboard EDA | 1 | Explorer, stats, graphiques, filtres | Six éléments déjà présents ; filtres et cas limites maintenant testés. **P1**, réalisé sur ce lot |
| 2.3 Prédiction | 1,5 | Formulaire et artefacts chargés | Absent ; formulaire + pipeline sauvegardé + validation d'entrée, sans entraînement interactif. **P0** |
| 3.1 Structure | 1 | data/notebooks/src/docs + dépendances | Dépendances restaurées, bytecode retiré ; fichiers standard manquants à créer sans dupliquer inutilement les CSV. **P1** |
| 3.2 Contributions | 2 | Contributeurs explicitement simulés | 34 commits, 3 auteurs, aucune PR et une seule branche distante. Vrais lots, relectures et comptes distincts à conserver. **P1**, continu |
| 4.1 Rapport PDF | 1,5 | Rapport de 40 pages | Rapport propre au projet absent ; assembler les sections de chacun avec chiffres réels. **P2** |
| 4.2 README | 1,5 | Installation, rôles, résultats | README remplacé par un guide vérifiable pour l'état réel du dépôt ; à compléter après les trois modèles et l'application. **P1** |

### Obligatoire et facultatif

Obligatoire : les six modèles ; optimisation des cinq modèles réglables ; au moins cinq plis ;
deux analyses justifiées ; les six éléments EDA ; application locale et prédiction ; rapport PDF ;
README ; arborescence ; contributions authentiques ; anonymat par codes.

L'hébergement en ligne est explicitement optionnel. Les six analyses, neuf pages d'interface,
XGBoost, stacking, SMOTE, PCA et 40 pages de rapport sont des caractéristiques de la référence,
pas des sous-critères chiffrés distincts dans la grille. Le texte « minimum attendu » autour
de l'exemple reste à clarifier avec le professeur ; il ne permet pas d'exiger les mêmes scores
sur un autre dataset. L'exemple utilise 9 000 lignes alors que le minimum explicite reste 10 000.
La grille /20 et la formule générale évoquant un projet /18 sont également à faire préciser.

### Ne pas recopier aveuglément le projet exemple

La référence est utile pour son organisation. Ses résultats n'ont pas été reproduits dans cet audit.
Dans la chaîne `scripts/train_pipeline.py` → `src/preprocessing.py` → `src/models.py`,
la transformation est ajustée avant les plis de recherche, et celle-ci se limite à 1 000 lignes,
malgré une présentation globale sur 7 200 lignes. Copier cette chaîne reproduirait une fuite
entre plis. Le prétraitement de votre recherche doit rester dans le Pipeline.
Le chargement de l'application de référence prévoit un réentraînement de secours : ne pas
copier ce comportement dans votre formulaire. Sa routine de correction FDR ne force pas
la monotonie des p-values ajustées ; votre correction de Holm existante est correcte.
Enfin, ses contributeurs simulés ne doivent jamais devenir un modèle d'historique pour le groupe.

## Résultats ML vérifiés

Validation **2024 uniquement**, classe positive = 1. Scores recalculés à partir des trois
artefacts sauvegardés, identiques aux CSV. La précision de Zero-R est fixée à 0 par convention
car il n'émet aucune alerte.

| Modèle | Accuracy | Précision | Rappel | F1 | ROC-AUC | TN / FP / FN / TP |
|---|---:|---:|---:|---:|---:|---|
| Zero-R | 0,9237 | 0,0000 | 0,0000 | 0,0000 | 0,5000 | 7780 / 0 / 643 / 0 |
| GaussianNB | 0,4811 | 0,1005 | 0,7294 | 0,1767 | 0,6299 | 3583 / 4197 / 174 / 469 |
| DecisionTree | 0,5572 | 0,0958 | 0,5692 | 0,1641 | 0,6092 | 4327 / 3453 / 277 / 366 |

Les 92,37 % de Zero-R ne traduisent pas une bonne détection : il rate tous les positifs.
NB retrouve davantage de positifs mais émet beaucoup de fausses alertes. Le F1 de sélection
CV vaut environ 0,410 pour NB et 0,423 pour l'arbre, contre 0,177 et 0,164 sur 2024.
L'écart nécessite une discussion, pas une sélection sur 2025. La fréquence de classe 1 dans
train est 27,23 %, contre 7,63 % sur la validation ; cela affecte notamment la précision et le F1.
Cette observation ne prouve pas à elle seule la cause de la baisse.

Les cinq plis sont : 2012–2018→2019, 2012–2019→2020, 2012–2020→2021,
2012–2021→2022, 2012–2022→2023. Les lignes de la même année restent ensemble.
Ce choix empêche l'entraînement sur le futur, mais n'est pas un K-Fold aléatoire classique.
Il vise de nouvelles années sur les zones représentées, pas des zones jamais observées.
Les méthodes de calcul des variables doivent également respecter le temps : de bons plis
ne suffisent pas à garantir l'absence de toutes les fuites.

Points ML restant à corriger :

- Harmoniser le protocole encore nommé `proposition_a_harmoniser` ; un notebook réécrit
  actuellement ce fichier partagé. Préférer une configuration centrale indépendante des résultats.
- Introduire un ColumnTransformer avec une liste explicite des 24 entrées, dans le Pipeline.
  Pas besoin d'inventer des catégories si les entrées sont toutes numériques.
- NB choisit `var_smoothing=0.01`, borne haute de sa grille. Étendre la recherche dans le train,
  avec les mêmes plis, est justifiable ; une amélioration n'est pas garantie.
- `var_smoothing` n'est pas le lissage de Laplace `alpha`. GaussianNB est adapté au type continu
  des entrées, même si ses hypothèses gaussiennes et d'indépendance restent approximatives.
- Le validateur de l'arbre doit refuser une liste de moins de cinq années ou des années dupliquées,
  et verrouiller les métadonnées/variables provisoirement exclues. Ces protections ne sont pas toutes présentes.
- L'arbre a été sauvegardé avec scikit-learn 1.9.1 ; NB et Zero-R avec 1.8.0.
  Le chargement de l'arbre en 1.8.0 a reproduit les chiffres mais émis un avertissement de version.
  Cela ne garantit pas la compatibilité : réentraîner les artefacts dans une version commune avant intégration.

## Statistiques : ce qui est conservé et ajouté

Les deux analyses principales restent fondées sur des écarts classe 1 moins classe 0
par zone/année, puis sur une moyenne à poids égal des zones par année.
Le test binomial porte sur les signes des 12 écarts annuels, pas sur 104 979 lignes indépendantes.

H0 : parmi les écarts annuels non nuls, la probabilité d'un signe positif est 0,5.
H1 : elle diffère de 0,5. Test bilatéral ; correction de Holm sur deux hypothèses.

| Analyse | Température maximale | Humidité moyenne | Signes annuels | p brute / p Holm |
|---|---:|---:|---|---|
| Principale, zone/année | +3,0769 unités CSV | −10,1067 points | 12/12 positifs ; 0/12 positifs | 0,00048828125 / 0,0009765625 |
| Sensibilité, zone/année/mois | +2,3071 unités CSV | −9,5909 points | 12/12 positifs ; 0/12 positifs | 0,00048828125 / 0,0009765625 |

La sensibilité moyenne d'abord les mois comparables dans une zone, puis les zones dans une année.
Elle limite un mélange de périodes différentes à l'intérieur d'une année. C'est un complément
exploratoire post hoc, pas un nouveau résultat confirmatoire indépendant. Les deux corrections
de Holm sont appliquées séparément par famille ; ne pas prétendre contrôler quatre hypothèses
confirmatoires à la fois. Les IC ajoutés portent sur la proportion de signes positifs,
pas sur l'écart moyen de température ou d'humidité.

L'indépendance entre années n'est pas démontrée. L'agrégation limite la pseudo-réplication
sans supprimer toutes les dépendances. Les négatifs sont sélectionnés ; on ne conclut
ni à une causalité ni au risque réel d'incendie. Les unités de température restent à certifier.

## Git et pondération individuelle

Au HEAD audité : **34 commits**, dont 31 pour le compte de IASD12, 2 pour le compte
de SIAD03 et 1 pour le compte de IASD17. Les deux autres codes proviennent de l'ancienne
application et restent à confirmer par leurs propriétaires. Une seule branche distante, `main` ;
aucune PR ouverte ou fermée retournée par GitHub. Aucune branche distante de travail non intégré
n'a été découverte. Cela ne renseigne pas sur leurs ordinateurs.

Pour SIAD03, l'API associe le commit de renommage au compte connecté ; le gros commit
`b1dc5f6` a un autre email d'auteur et l'API ne l'associe pas à un utilisateur GitHub.
Vérifier dans GitHub si cet email appartient bien à SIAD03 et est vérifié. S'il lui appartient,
son ajout au compte peut aider l'attribution ; **ne pas réécrire l'historique**.
Ce constat ne prouve pas la formule de la plateforme du professeur.

La commande `git log --all --numstat` inclut des volumes de CSV et la représentation JSON
des notebooks. Les comptes bruts d'ajouts/suppressions ne sont donc pas une mesure fiable
de travail scientifique. Par exemple, le commit SIAD03 contient 121 870 lignes de CSV propre.
Ne pas multiplier les exports, les lignes ou les commits pour influer artificiellement sur la note.

La capture fournie décrit : impact élevé ≥75 % du « fair share », poids 100 % ; impact modéré
35–74 %, poids 60–90 % ; impact faible 1–34 %, poids 20–50 % ; impact nul, note 0.
Si le partage équitable est exactement 1/3, le seuil élevé représente
`0,75 × 1/3 = 0,25`, soit **25 % du travail total**. Mais 25 % du « fair share »
représenterait seulement 8,33 % du total. Sans le libellé et la formule du score affiché,
on ne peut pas classer définitivement l'étudiant ni calculer sa note individuelle.

Il reste aussi une non-conformité d'anonymat : des prénoms sont présents dans les chemins,
le plan PDF et certains textes existants. Préparer une version publique par codes, en conservant
les originaux internes. Les nouveaux documents de ce lot utilisent SIAD03 et les codes historiques.

## Plan priorisé et répartition

| Lot | Responsable proposé | Livraison vérifiable | Critères concernés |
|---|---|---|---|
| 1 — Qualité, EDA, analyses | SIAD03 | Contrôles intégrés, audit CLI, sensibilité mensuelle, filtres testés ; livré localement dans ce lot | 1.1, 1.2, 2.2, 3.1, 4.2 |
| 2 — Protocole et modèles manquants | IASD12 | Configuration centrale, Pipeline/ColumnTransformer, K-NN et SVM réglés sur cinq plis temporels, métriques communes | 1.1, 1.3, 1.4, 1.5 |
| 3 — Forêt et intégration | IASD17 | Random Forest réglée, compatibilité de l'arbre, app principale, comparaison et formulaire | 1.3, 1.4, 1.5, 2.1, 2.3 |
| 4 — NB et preuves personnelles | SIAD03 | Script entraînement NB/Zero-R, grille élargie justifiée, sélection par train/CV, tests de sauvegarde, sections scientifiques | 1.2, 1.4, 1.5, 3.2, 4.1 |
| 5 — Rendu commun | Tous ; assemblage IASD17 | Rapport PDF, anonymat, README final, test sur copie fraîche, gel puis évaluation 2025 | 3.1, 3.2, 4.1, 4.2 |

Ce sont des propositions de répartition ; aucune tâche n'a été envoyée à un coéquipier.
SIAD03 fournit `render_eda(df)` ; IASD17 importe ce composant dans l'application.
IASD12 définit le format commun des artefacts et métriques avant leur intégration.
Ne pas modifier simultanément un notebook partagé. Ouvrir ensuite des PR limitées et relues.

## Premier lot implémenté

- `src/data_quality.py`, `src/cleaning_guide.py` : schéma minimal, nombres, dates,
  incohérences physiques, valeurs infinies ; erreurs lisibles ; NaN et code 9999 conservés.
- `src/audit_data.py` : commande d'audit, empreinte brute, tableaux de fuites et compteurs.
- `src/statistical_analysis.py` : analyse principale reproduite, sensibilité mensuelle,
  Holm robuste aux tests non calculables et IC des signes.
- `src/eda_view.py`, `src/run_eda_demo.py` : filtres années/classes/mois/zones,
  boxplots, commentaires, traitement du résultat vide et erreurs de chargement.
- `tests/` : tests de corruption des données, non-modification du brut, doublons,
  absence d'usage du futur dans les analyses, Holm, saisonnalité et interactions Streamlit.
- `requirements*.txt`, `.gitignore` : installation versionnée ; bytecode suivi retiré.
- `README.md`, ce document et les guides associés : procédures, responsabilités,
  résultats vérifiés et limites explicites.

Les notebooks, les données et les modèles existants ne sont pas écrasés.
Les nouveaux résultats sont isolés dans `results/audit_siad03/`.

## Validation et limites du lot

Environnement neuf : Python 3.12.14, installation des versions de `requirements-dev.txt`.
**31 tests réussis** au premier passage ; la preuve finale est dans `results/audit_siad03/verification_lot.json`.
Les tests Streamlit utilisent AppTest sur le vrai fichier et sur des cas limites.
Ils vérifient les interactions sans constituer une inspection manuelle dans un navigateur.
Les six figures sauvegardées ont été inspectées.

Les cellules des deux notebooks ont été réexécutées dans l'ordre, dans une copie isolée :
12 cellules Python pour l'EDA et 9 pour Zero-R/NB. Le noyau Jupyter n'a pas pu démarrer
à cause d'une restriction réseau de l'environnement ; l'exécution séquentielle Python
a donc été utilisée. Aucun score 2025 n'a été calculé.

Les scores sauvegardés des trois modèles ont été recalculés ; les cinq plis et les deux
analyses principales ont été comparés aux fichiers existants. La recherche complète de l'arbre
n'a pas été relancée. Les avertissements de version de son artefact sont conservés dans la preuve.

Le projet complet reste **partiellement conforme**. L'absence de trois modèles, du formulaire,
de l'application principale, du rapport final et de preuves Git futures interdit d'annoncer 100 %.

## Références techniques

- [Validation temporelle scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-of-time-series-data)
- [GridSearchCV et indices personnalisés de plis](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
- [Test binomial exact SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
