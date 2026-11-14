> Document historique fourni dans corrections_SIAD03.zip. Les indications « aucun commit », les commandes d’intégration et les validations de notebooks concernent le lot d’origine. Pour cette intégration locale, consulter le README et l’historique Git ; aucun push effectué.

# Valider les données et tester les analyses et filtres EDA

Le nettoyage acceptait des valeurs physiquement incohérentes alors que le notebook les comptait. La démo n'expliquait pas les erreurs de chargement et aucun test ne couvrait ses filtres.

Ce lot ajoute des contrôles réutilisables, un audit avec empreinte du brut, une sensibilité statistique par mois et des tests Streamlit. Les filtres années/classes/mois/zones s'appliquent à toutes les sorties. Notebooks, données et modèles sont conservés ; nouveaux résultats dans `results/audit_siad03/`.

Validation Python 3.12 dans un environnement neuf : 31 tests ; CSV nettoyé identique ; statistiques principales et métriques de trois artefacts reproduites sur 2024 ; 21 cellules de notebooks exécutées séquentiellement en Python. Aucun score calculé sur 2025.

Limites : noyau Jupyter indisponible dans l'environnement d'audit ; AppTest ne constitue pas une inspection visuelle Windows ; ancien artefact arbre sauvegardé sous une autre version scikit-learn. Trois modèles, l'application complète et le rapport final restent à intégrer.

README et audit décrivent l'état partiel et le plan de rattrapage. Les fichiers bytecode générés sont retirés du suivi prévu. Aucun historique n'est réécrit.
