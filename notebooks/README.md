# Notebooks

This folder contains Jupyter notebooks for the EV data analysis pipeline.

## Quick Start

After downloading raw data (see `data/README.md`), run notebooks in the following order:

### Phase 1: Data Preparation (Cleaning & Wrangling)

1. **`data_cleaning/dp_fill_2024.ipynb`** - Fill missing 2024 data in IEA dataset
2. **`data_wrangling/merge_ev_stations.ipynb`** - Merge international + China charging stations
3. **`data_wrangling/transform_data.ipynb`** - Transform IEA data to wide format
4. **`merge_datasets.ipynb`** - Combine EV sales data with station statistics

After `merge_datasets.ipynb` has produced `data/processed/merged_dataset.csv`, run:

- **`data_wrangling/calculate_metrics.py`** - One-time metrics script that derives growth, infrastructure adequacy, and correlation metrics under `data/processed/metrics/` (including `correlation_data.csv` used by `ev.ipynb` and the dashboard).

### Phase 2: Core Analysis & Visualization

Once data preparation is complete, run these main notebooks:

5. **`ev.ipynb`** ⭐ **MAIN NOTEBOOK** - Comprehensive EDA with interactive charts:

   - Time-series analysis (EV adoption trends 2010-2023)
   - Geographic heatmaps (regional distribution)
   - Infrastructure analysis (charging stations vs EVs)
   - Powertrain comparisons (BEV vs PHEV)
   - Linked dashboard views

6. **`data_visualization/ev_stations_map.ipynb`** ⭐ **MAIN VISUALIZATION** - Interactive global map:
   - 12,002 charging stations with marker clustering
   - Rich popups with station details
   - Status indicators and operator icons
   - Exports to standalone HTML

## Notebook Descriptions

| Notebook / Script                 | Stage         | Purpose                                                           | Input                                                        | Output                                                            |
| --------------------------------- | ------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------- |
| `dp_fill_2024.ipynb`              | Cleaning      | Fill Year 2024 gaps using interpolation/forward-fill              | `raw/IEA Global EV Data 2024.csv`                            | `processed/IEA_Global_EV_Data_2024_filled.csv`                    |
| `merge_ev_stations.ipynb`         | Wrangling     | Merge international + Chinese station data                        | `raw/ev_stations_2025.csv`, Chinese dataset                  | `processed/merged_charging_station/ev_stations_merged_global.csv` |
| `transform_data.ipynb`            | Wrangling     | Pivot long-to-wide format                                         | `raw/IEA Global EV Data 2024.csv`                            | `processed/iea_wide_format.csv`                                   |
| `merge_datasets.ipynb`            | Integration   | Join EV data with station stats                                   | `processed/IEA_Global_EV_Data_2024_filled.csv`, station data | `processed/merged_dataset.csv`                                    |
| `calculate_metrics.py`            | Metrics       | Derive growth, infrastructure adequacy, and correlation metrics   | `processed/merged_dataset.csv`                               | `processed/metrics/*.csv` (e.g. `correlation_data.csv`)           |
| `ev.ipynb`                        | EDA           | Time-series, choropleth, infrastructure adequacy scatter, sunburst charts | Processed CSVs incl. `processed/metrics/correlation_data.csv` | Inline visualizations                                             |
| `ev_stations_map.ipynb`           | Visualization | Interactive Folium map                                            | `ev_stations_merged_global.csv`                              | `output/ev_stations_global_map.html`                              |

## Pipeline Flow

```
RAW DATA (downloaded manually)
    ├── IEA Global EV Data 2024.csv
    ├── ev_stations_2025.csv
    └── CnOpenData全国充电站分布数据（样本数据）.xlsx
         |
         v
    PHASE 1: CLEANING & WRANGLING
         |
    ┌────┴────────────────────────────┐
    |                                  |
[dp_fill_2024]              [merge_ev_stations]
    |                                  |
    v                                  v
IEA_filled.csv            ev_stations_merged_global.csv
    |                                  |
[transform_data]                      |
    |                                  |
    v                                  |
iea_wide_format.csv                   |
    |                                  |
    └──────────┬───────────────────────┘
               v
       [merge_datasets]
               |
               v
       merged_dataset.csv
               |
         ┌─────┴─────┐
         v           v
    PHASE 2: MAIN ANALYSIS
         |           |
    [ev.ipynb]  [ev_stations_map.ipynb]
         |           |
         v           v
   Dashboards    Interactive Map
   & Charts      (HTML output)
```

## Folder Structure

```
notebooks/
  ev.ipynb                    # Main EDA notebook (uses metrics from calculate_metrics.py)
  merge_datasets.ipynb        # Data integration
  data_cleaning/
    dp_fill_2024.ipynb        # Year 2024 data filling
  data_wrangling/
    merge_ev_stations.ipynb   # Station data merge
    transform_data.ipynb      # Format transformation
    calculate_metrics.py      # One-time metrics calculation script
  data_visualization/
    ev_stations_map.ipynb     # Interactive map
```
