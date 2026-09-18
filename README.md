
## Project

**Type:** School Data Mining Project
**Domain:** Wildfire Risk Analysis
**Dataset:** Algeria Wildfire Risk — 121k Labelled Cell-Days

The project uses this dataset as a foundation for **exploratory data analysis, feature analysis, pattern discovery, and machine learning experiments**.



# Algeria Wildfire Risk: 121k Labelled Cell-Days

## Motivation

Wildfire prediction is a challenging data mining problem because fire occurrence depends on the interaction of weather, atmospheric dryness, vegetation, and temporal conditions.

This dataset provides a rich real-world basis for studying these relationships and exploring how data mining and machine learning can be applied to wildfire risk analysis.

This repository is part of a **school Data Mining project**, where the dataset is used to investigate patterns and relationships associated with wildfire occurrence in Algeria.

## Dataset Overview

The dataset contains **121,869 labelled cell-days** representing observations across approximately **1,423 spatial cells** and **14 fire seasons (2012–2025)**, mainly covering June to October.

Each row represents a `(cell_id, date)` observation.

| Property           | Description                                           |
| ------------------ | ----------------------------------------------------- |
| Rows               | 121,869                                               |
| Columns            | 37                                                    |
| Spatial resolution | 0.1° cells                                            |
| Number of cells    | ~1,423                                                |
| Period             | 2012–2025                                             |
| Fire seasons       | 14                                                    |
| Observation unit   | Cell × Day                                            |
| Data type          | Weather, FWI, vegetation and fire-related information |

## Data Sources

The dataset combines information from several scientific data sources:

| Source                 | Information                        |
| ---------------------- | ---------------------------------- |
| NASA FIRMS             | Satellite fire detections          |
| ERA5-Land / Open-Meteo | Weather and atmospheric conditions |
| MODIS                  | Vegetation indices (NDVI)          |

The original dataset is available on [Kaggle](https://www.kaggle.com/datasets/abdelmaleknedjar/algeria-wildfire-risk-121k-labelled-cell-days?utm_source=chatgpt.com).

## Main Columns

The 37 columns can be grouped into several categories:

| Category           | Examples                                                                             |
| ------------------ | ------------------------------------------------------------------------------------ |
| Spatial & temporal | `cell_id`, `lat`, `lon`, `date`, `year`, `doy`                                       |
| Fire information   | `label`, `sample_kind`, `n_detections`, `max_frp`                                    |
| Weather            | `temp_max`, `temp_min`, `temp_mean`, `rh_mean`, `wind_mean`, `precip_sum`, `vpd_max` |
| Antecedent dryness | `precip_7d`, `precip_30d`, `days_since_rain_1mm`                                     |
| Fire Weather Index | `ffmc`, `dmc`, `dc`, `isi`, `bui`, `fwi`                                             |
| Fuel conditions    | `days_since_last_fire`                                                               |
| Vegetation         | `ndvi`, `ndvi_normal`, `ndvi_anomaly`, `ndvi_change_32d`, `ndvi_stale_days`          |
| Dataset split      | `split`                                                                              |

## Dataset Structure

The dataset is a **sampled panel** rather than a conventional scraped dataset. It combines spatial and temporal observations, allowing each cell to be studied across multiple dates and fire seasons.

This structure makes the dataset suitable for exploring how environmental and temporal variables relate to wildfire occurrence.
