> Document historique fourni dans corrections_SIAD03.zip. Les indications « aucun commit », les commandes d’intégration et les validations de notebooks concernent le lot d’origine. Pour cette intégration locale, consulter le README et l’historique Git ; aucun push effectué.

# Intégrer le premier lot SIAD03 dans VS Code

Base : `d8d06a9469c4ccdf0b51c24cbd5a961816da7e76`. Aucun nouveau commit ni push. Le compte GitHub a été vérifié et le code SIAD03 confirmé. La configuration du clone d'audit ne modifie pas celle du PC.

## 1. Utiliser une copie séparée

Ne pas remplacer un dossier contenant des modifications non sauvegardées. Dans un nouveau dossier, sous PowerShell :

```powershell
git clone https://github.com/hani231/Algeria-Wildfire-Risk-121k-Labelled-Cell-Days.git wildfire-siad03
cd wildfire-siad03
git status --short
git switch -c feature/SIAD03-audit-eda d8d06a9469c4ccdf0b51c24cbd5a961816da7e76
```

Extraire `corrections_SIAD03.zip` ailleurs et adapter le chemin réel :

```powershell
git apply --check "C:\CHEMIN\corrections_SIAD03\changes.patch"
git apply "C:\CHEMIN\corrections_SIAD03\changes.patch"
git diff --stat
git status --short
```

Si le contrôle échoue, arrêter et comparer les versions, sans forcer. `files/` contient les fichiers complets ajoutés/modifiés ; `manifest.json` liste aussi les suppressions de bytecode. Ne pas remplacer tout le dépôt par l'archive.

## 2. Installer et tester

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.audit_data
.\.venv\Scripts\python.exe -m src.verify_existing
.\.venv\Scripts\python.exe -m src.statistical_analysis
.\.venv\Scripts\python.exe -m streamlit run src/run_eda_demo.py
```

Changer année, classe, mois et zone dans la démo : tous les effectifs et graphiques doivent suivre. Retirer toutes les classes doit afficher « Aucune observation ». Aucune interaction n'entraîne de modèle.

## 3. Comprendre les modifications

- Une humidité à 101 %, un vent négatif ou une valeur infinie sont rejetés.
- Un NDVI manquant reste un NaN ; l'imputation relève du pipeline ML.
- 9999 reste un code spécial, pas une durée réelle.
- La sensibilité mensuelle compare les classes dans une même zone/année/mois, puis moyenne les mois par zone et les zones par année.
- Le test des signes porte sur les années. Holm corrige les deux tests de chaque analyse.
- Les filtres restent limités au train et s'appliquent à toutes les sorties.

## 4. Préparer le commit après relecture

Vérifier l'identité Git du PC. L'email doit appartenir réellement au compte GitHub et être vérifié dans ses paramètres ; ne pas utiliser celui d'un coéquipier.

```powershell
git config --local user.name
git config --local user.email
git config --local user.name "SIAD03"
git diff --check
git diff -- src/cleaning_guide.py src/eda_view.py src/run_eda_demo.py
```

Un seul commit pour ce lot cohérent est acceptable. Ces commandes sont proposées, pas exécutées :

```powershell
git add .gitignore requirements.txt requirements-dev.txt README.md src/data_quality.py src/audit_data.py src/verify_existing.py src/statistical_analysis.py src/cleaning_guide.py src/eda_view.py src/run_eda_demo.py tests docs/AUDIT_SIAD03.md docs/MATRICE_CONFORMITE.csv docs/INTEGRATION_SIAD03.md docs/PR_SIAD03.md results/audit_siad03
git add -u src/__pycache__
git diff --cached --stat
git commit -m "fix(SIAD03): valider les donnees et tester les analyses et filtres EDA"
```

Ajouter les preuves de l'exécution Windows à la PR. `docs/PR_SIAD03.md` propose une description. La publication reste une étape distincte.

## 5. Retrouver le travail historique

```powershell
git show --stat b1dc5f6
git show 8e87fcb:UI/app.py
git show 8e87fcb:README.md
```

Ces commandes consultent sans écraser. Décider ensemble des éléments à restaurer. L'ancienne interface ne prédisait rien : sa restauration ne suffit pas au critère 2.3. L'ancien notebook contient des expériences à conserver et des transformations à revoir.

Prochaine contribution SIAD03 : script Zero-R/NB, ColumnTransformer commun, grille NB élargie dans les cinq plis temporels, métadonnées d'artefacts et rédaction scientifique. Ne pas utiliser 2025 pour sélectionner les réglages.
