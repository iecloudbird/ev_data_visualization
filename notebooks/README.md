# Notebooks

This folder contains Jupyter notebooks for the EV data analysis pipeline.

## Pipeline Overview

The notebooks follow an end-to-end pipeline:

```
Ingestion -> Cleaning -> Wrangling -> EDA/Analysis -> Visualization
```

## Execution Order

Run notebooks in this order:

1. `data_cleaning/dp_fill_2024.ipynb` - Fill missing 2024 data
2. `data_wrangling/merge_ev_stations.ipynb` - Merge charging station datasets
3. `data_wrangling/transform_data.ipynb` - Transform to wide format
4. `merge_datasets.ipynb` - Combine EV and station data
5. `ev.ipynb` - Main EDA and visualization
6. `data_visualization/ev_stations_map.ipynb` - Interactive map

## Notebook Descriptions

| Notebook                  | Stage         | Purpose                                              | Input                                                        | Output                                                            |
| ------------------------- | ------------- | ---------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------- |
| `dp_fill_2024.ipynb`      | Cleaning      | Fill Year 2024 gaps using interpolation/forward-fill | `raw/IEA Global EV Data 2024.csv`                            | `processed/IEA_Global_EV_Data_2024_filled.csv`                    |
| `merge_ev_stations.ipynb` | Wrangling     | Merge international + Chinese station data           | `raw/ev_stations_2025.csv`, Chinese dataset                  | `processed/merged_charging_station/ev_stations_merged_global.csv` |
| `transform_data.ipynb`    | Wrangling     | Pivot long-to-wide format                            | `raw/IEA Global EV Data 2024.csv`                            | `processed/iea_wide_format.csv`                                   |
| `merge_datasets.ipynb`    | Integration   | Join EV data with station stats                      | `processed/IEA_Global_EV_Data_2024_filled.csv`, station data | `processed/merged_dataset.csv`                                    |
| `ev.ipynb`                | EDA           | Time-series, choropleth, sunburst charts             | Processed CSVs                                               | Inline visualizations                                             |
| `ev_stations_map.ipynb`   | Visualization | Interactive Folium map                               | `ev_stations_merged_global.csv`                              | `output/ev_stations_global_map.html`                              |

## Pipeline Flow

```
RAW DATA
    |
    v
[dp_fill_2024.ipynb] --> IEA_Global_EV_Data_2024_filled.csv
    |
[merge_ev_stations.ipynb] --> ev_stations_merged_global.csv
    |
[transform_data.ipynb] --> iea_wide_format.csv
    |
    v
[merge_datasets.ipynb] --> merged_dataset.csv
    |
    v
[ev.ipynb] --> Charts & Analysis
    |
[ev_stations_map.ipynb] --> Interactive HTML Map
```

## Folder Structure

```
notebooks/
  ev.ipynb                    # Main EDA notebook
  merge_datasets.ipynb        # Data integration
  data_cleaning/
    dp_fill_2024.ipynb        # Year 2024 data filling
  data_wrangling/
    merge_ev_stations.ipynb   # Station data merge
    transform_data.ipynb      # Format transformation
  data_visualization/
    ev_stations_map.ipynb     # Interactive map
```
