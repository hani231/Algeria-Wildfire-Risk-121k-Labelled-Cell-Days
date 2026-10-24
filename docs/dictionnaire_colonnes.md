# Dictionnaire des 37 colonnes

Descriptions fondées sur le README et le notebook fournis. Les calculs et conventions du producteur ne sont pas inclus dans l’archive. Les unités non établies y sont signalées plutôt qu’inventées.

| Colonne | Sens | Unité / format | Utilisation |
|---|---|---|---|
| cell_id | Identifiant de la cellule géographique. Plusieurs dates par cellule. | identifiant | Métadonnée ; conserver pour les contrôles et groupes. |
| lat | Latitude du centre de la cellule. | degrés | Cartographie ; exclue du modèle proposé. |
| lon | Longitude du centre de la cellule. | degrés | Cartographie ; exclue du modèle proposé. |
| date | Date de l’observation cellule-jour. | AAAA-MM-JJ | Métadonnée temporelle. |
| year | Année de la date. | année | Partition et plis ; exclue des entrées proposées. |
| doy | Numéro du jour dans l’année. | 1 à 365/366 | Entrée saisonnière proposée. |
| label | Cible : 1 = détection, 0 = absence de détection dans ce jeu. | 0 ou 1 | y ; jamais dans X. |
| sample_kind | Type de sélection de la ligne : positive ou matched_negative. | catégorie | Exclure de X : fuite démontrée. |
| n_detections | Nombre de détections associées à la cellule et au jour. | compte | Exclure de X : fuite démontrée. |
| max_frp | Puissance radiative maximale des détections du jour. | unité à confirmer | Exclure de X : fuite démontrée ; NaN pour tous les négatifs. |
| temp_max | Température maximale du jour. | unité source à confirmer (probablement °C) | Entrée proposée pour classification rétrospective. |
| temp_min | Température minimale du jour. | unité source à confirmer (probablement °C) | Entrée proposée. |
| temp_mean | Température moyenne du jour. | unité source à confirmer (probablement °C) | Entrée proposée. |
| rh_min | Humidité relative minimale du jour. | % | Entrée proposée. |
| rh_mean | Humidité relative moyenne du jour. | % | Entrée proposée. |
| wind_max | Vitesse maximale du vent. | unité source à confirmer | Ne pas supposer km/h ou m/s dans le formulaire. |
| wind_mean | Vitesse moyenne du vent. | unité source à confirmer | Entrée proposée ; unité à confirmer. |
| precip_sum | Précipitations cumulées du jour. | unité source à confirmer (probablement mm) | Entrée proposée. |
| vpd_max | Déficit maximal de pression de vapeur ; mesure de la demande de dessèchement. | unité source à confirmer | Ne pas supposer kPa ou hPa. |
| precip_7d | Cumul des précipitations sur une fenêtre passée de 7 jours selon le notebook existant. | même unité que precip_sum | Confirmer les bornes exactes de la fenêtre. |
| precip_30d | Cumul des précipitations sur une fenêtre passée de 30 jours selon le notebook existant. | même unité que precip_sum | Confirmer les bornes exactes de la fenêtre. |
| days_since_rain_1mm | Nombre de jours depuis une pluie atteignant le seuil de 1 mm. | jours | Entrée proposée ; vérifier convention jour courant. |
| temp_max_7d_mean | Moyenne récente de temp_max sur 7 jours. | même unité que temp_max | Vérifier que la fenêtre utilise uniquement le passé autorisé. |
| rh_min_7d_mean | Moyenne récente de rh_min sur 7 jours. | % | Vérifier la fenêtre. |
| ffmc | Fine Fuel Moisture Code : état de sécheresse des combustibles fins. | indice | Ne pas imposer un seuil externe sans vérifier l’implémentation. |
| dmc | Duff Moisture Code : humidité/sécheresse de la couche organique. | indice | Entrée proposée. |
| dc | Drought Code : composante de sécheresse à plus long terme. | indice | Entrée proposée. |
| isi | Initial Spread Index : potentiel initial de propagation. | indice | Entrée proposée. |
| bui | Buildup Index : disponibilité estimée des combustibles. | indice | Entrée proposée. |
| fwi | Indice global du système Fire Weather Index. | indice | Ce n’est pas une probabilité d’incendie. |
| days_since_last_fire | Jours depuis le dernier feu antérieur connu selon le notebook existant. | jours ; 9999 = code spécial à confirmer | Exclu provisoirement du modèle : confirmer historique et sentinelle. |
| split | Partition du dataset : train, val ou test. | catégorie | Métadonnée ; jamais dans X. |
| ndvi | Indice de végétation décrivant sa verdure. | sans unité | Entrée proposée ; confirmer date de disponibilité de la mesure. |
| ndvi_normal | NDVI de référence historique pour la zone et la période. | sans unité | Exclu provisoirement : vérifier la période de calcul sans futur. |
| ndvi_anomaly | Écart entre NDVI et sa normale. | sans unité | Exclu provisoirement tant que la normale n’est pas vérifiée. |
| ndvi_change_32d | Variation du NDVI sur environ 32 jours. | sans unité | Entrée proposée ; confirmer disponibilité passée. |
| ndvi_stale_days | Âge de l’information NDVI associée à la ligne. | jours | Entrée proposée ; grande valeur = mesure ancienne, pas automatiquement erreur. |

Source originale annoncée dans le README : [Kaggle](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days). La page n’a pas fourni de fiche lisible lors de la vérification ; les détails manquants restent à confirmer auprès du producteur.
