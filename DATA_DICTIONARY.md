# EV Data Visualization – Data Dictionary

This document lists the main data sources used in the EV Dashboard project, with fields, inferred types (from pandas dtypes), brief descriptions, and the dataset source.

---

## Dataset: `data/raw/IEA Global EV Data 2024.csv`

Long-format IEA global EV dataset (raw input).

| Field      | Type    | Description                                                                 | Source file                               |
|-----------|---------|-------------------------------------------------------------------------------|-------------------------------------------|
| region    | object  | Geographic region or market (e.g., country or aggregate region).            | data/raw/IEA Global EV Data 2024.csv      |
| category  | object  | High-level data category (e.g., sales, stock, infrastructure).              | data/raw/IEA Global EV Data 2024.csv      |
| parameter | object  | Specific metric within the category (e.g., EV sales, EV stock).             | data/raw/IEA Global EV Data 2024.csv      |
| mode      | object  | Transport mode (e.g., road, two/three-wheelers, buses).                     | data/raw/IEA Global EV Data 2024.csv      |
| powertrain| object  | Vehicle powertrain type (e.g., BEV, PHEV, FCEV).                             | data/raw/IEA Global EV Data 2024.csv      |
| year      | int64   | Calendar year for the observation.                                          | data/raw/IEA Global EV Data 2024.csv      |
| unit      | object  | Unit of measurement for `value` (e.g., vehicles, %, GWh).                   | data/raw/IEA Global EV Data 2024.csv      |
| value     | float64 | Measured value for the specified dimension (region/category/parameter/etc.).| data/raw/IEA Global EV Data 2024.csv      |

---

## Dataset: `data/processed/IEA_Global_EV_Data_2024_filled.csv`

IEA data with gaps for 2024 filled via interpolation/forward-fill.

| Field       | Type    | Description                                                                                  | Source file                                  |
|------------|---------|----------------------------------------------------------------------------------------------|----------------------------------------------|
| region     | object  | Geographic region or market.                                                                 | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| category   | object  | High-level data category.                                                                    | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| parameter  | object  | Specific metric within the category.                                                         | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| mode       | object  | Transport mode.                                                                              | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| powertrain | object  | Vehicle powertrain type.                                                                     | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| year       | int64   | Calendar year for the observation.                                                          | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| unit       | object  | Unit of measurement for `value`.                                                             | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| value      | float64 | Filled numeric value (including imputed 2024 values).                                       | data/processed/IEA_Global_EV_Data_2024_filled.csv |
| fill_method| object  | Method used to fill gaps (e.g., interpolation, forward_fill, original).                      | data/processed/IEA_Global_EV_Data_2024_filled.csv |

---

## Dataset: `data/processed/iea_wide_format.csv`

Pivoted wide-format IEA dataset used for analysis and visualizations.

| Field                         | Type    | Description                                                                 | Source file                         |
|------------------------------|---------|-----------------------------------------------------------------------------|-------------------------------------|
| region                       | object  | Geographic region or market.                                               | data/processed/iea_wide_format.csv  |
| year                         | int64   | Calendar year.                                                             | data/processed/iea_wide_format.csv  |
| category                     | object  | High-level data category.                                                  | data/processed/iea_wide_format.csv  |
| mode                         | object  | Transport mode.                                                            | data/processed/iea_wide_format.csv  |
| powertrain                   | object  | Vehicle powertrain type.                                                   | data/processed/iea_wide_format.csv  |
| ev_charging_points           | float64 | Number of public EV charging points.                                      | data/processed/iea_wide_format.csv  |
| ev_sales                     | float64 | Number of EVs sold in the year.                                           | data/processed/iea_wide_format.csv  |
| ev_sales_share               | float64 | EV sales as a share of total vehicle sales.                               | data/processed/iea_wide_format.csv  |
| ev_stock                     | float64 | Total EV stock (cumulative EVs on the road).                              | data/processed/iea_wide_format.csv  |
| ev_stock_share               | float64 | EV stock as a share of total vehicle stock.                               | data/processed/iea_wide_format.csv  |
| electricity_demand           | float64 | Electricity demand associated with EVs.                                   | data/processed/iea_wide_format.csv  |
| oil_displacement_mbd         | float64 | Oil displacement in million barrels per day.                              | data/processed/iea_wide_format.csv  |
| oil_displacement,_million_lge| float64 | Oil displacement in million litres of gasoline equivalent (LGE).          | data/processed/iea_wide_format.csv  |

---

## Dataset: `data/raw/ev_stations_2025.csv`

International EV charging stations dataset (raw input).

| Field          | Type    | Description                                                             | Source file                    |
|---------------|---------|-------------------------------------------------------------------------|--------------------------------|
| id            | int64   | Unique identifier of the charging station record.                      | data/raw/ev_stations_2025.csv |
| title         | object  | Name of the charging station or site.                                  | data/raw/ev_stations_2025.csv |
| address       | object  | Street address of the station.                                         | data/raw/ev_stations_2025.csv |
| town          | object  | Town or city where the station is located.                             | data/raw/ev_stations_2025.csv |
| state         | object  | State, province, or region.                                            | data/raw/ev_stations_2025.csv |
| postcode      | object  | Postal or ZIP code.                                                    | data/raw/ev_stations_2025.csv |
| country       | object  | Country name.                                                          | data/raw/ev_stations_2025.csv |
| lat           | float64 | Latitude coordinate of the station.                                    | data/raw/ev_stations_2025.csv |
| lon           | float64 | Longitude coordinate of the station.                                   | data/raw/ev_stations_2025.csv |
| operator      | object  | Company or organization operating the station.                         | data/raw/ev_stations_2025.csv |
| status        | object  | Operational status (e.g., operational, planned, closed).               | data/raw/ev_stations_2025.csv |
| num_connectors| int64   | Number of charging connectors available at the station.                | data/raw/ev_stations_2025.csv |
| connector_types| object | Types of connectors (e.g., CCS, CHAdeMO, Type 2).                      | data/raw/ev_stations_2025.csv |
| date_added    | object  | Date the station was added to the dataset or network (string format). | data/raw/ev_stations_2025.csv |

---

## Dataset: `data/processed/merged_charging_station/ev_stations_merged_global.csv`

Merged global charging stations dataset combining international and Chinese sources.

| Field          | Type    | Description                                                             | Source file                                               |
|---------------|---------|-------------------------------------------------------------------------|-----------------------------------------------------------|
| id            | int64   | Unique identifier of the charging station record.                      | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| title         | object  | Name of the charging station or site.                                  | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| address       | object  | Street address of the station.                                         | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| town          | object  | Town or city where the station is located.                             | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| state         | object  | State, province, or region.                                            | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| postcode      | object  | Postal or ZIP code.                                                    | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| country       | object  | Country name.                                                          | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| lat           | float64 | Latitude coordinate of the station.                                    | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| lon           | float64 | Longitude coordinate of the station.                                   | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| operator      | object  | Company or organization operating the station.                         | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| status        | object  | Operational status (e.g., operational, planned, closed).               | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| num_connectors| int64   | Number of charging connectors available at the station.                | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| connector_types| object | Types of connectors (e.g., CCS, CHAdeMO, Type 2).                      | data/processed/merged_charging_station/ev_stations_merged_global.csv |
| date_added    | object  | Date the station was added to the dataset or network (string format). | data/processed/merged_charging_station/ev_stations_merged_global.csv |

---

## Dataset: `data/processed/merged_dataset.csv`

Main merged dataset combining EV stats with aggregated charging station metrics used by the dashboard.

| Field                         | Type    | Description                                                                 | Source file                      |
|------------------------------|---------|-----------------------------------------------------------------------------|----------------------------------|
| region                       | object  | Geographic region or market.                                               | data/processed/merged_dataset.csv|
| year                         | int64   | Calendar year.                                                             | data/processed/merged_dataset.csv|
| category                     | object  | High-level data category.                                                  | data/processed/merged_dataset.csv|
| mode                         | object  | Transport mode.                                                            | data/processed/merged_dataset.csv|
| powertrain                   | object  | Vehicle powertrain type.                                                   | data/processed/merged_dataset.csv|
| ev_charging_points           | float64 | Number of public EV charging points.                                      | data/processed/merged_dataset.csv|
| ev_sales                     | float64 | Annual number of EVs sold.                                                | data/processed/merged_dataset.csv|
| ev_sales_share               | float64 | Share of EVs in total vehicle sales.                                      | data/processed/merged_dataset.csv|
| ev_stock                     | float64 | Total EV stock (cumulative vehicles on the road).                          | data/processed/merged_dataset.csv|
| ev_stock_share               | float64 | EV stock as a share of total vehicle stock.                               | data/processed/merged_dataset.csv|
| electricity_demand           | float64 | Electricity demand associated with EVs.                                   | data/processed/merged_dataset.csv|
| oil_displacement_mbd         | float64 | Oil displacement in million barrels per day.                              | data/processed/merged_dataset.csv|
| oil_displacement,_million_lge| float64 | Oil displacement in million litres of gasoline equivalent (LGE).          | data/processed/merged_dataset.csv|
| total_stations               | float64 | Total number of charging stations for the region.                         | data/processed/merged_dataset.csv|
| unique_operators             | float64 | Number of unique station operators in the region.                         | data/processed/merged_dataset.csv|
| operational_ratio            | float64 | Proportion of stations marked as operational.                             | data/processed/merged_dataset.csv|
| avg_connectors               | float64 | Average number of connectors per station.                                 | data/processed/merged_dataset.csv|
| stations_per_million_evs     | float64 | Stations per million EVs (infrastructure density metric).                 | data/processed/merged_dataset.csv|

---

## Dataset: `data/processed/metrics/bev_phev_market_share.csv`

Market share metrics for BEV vs PHEV sales by region and year.

| Field                 | Type    | Description                                                          | Source file                                      |
|-----------------------|---------|----------------------------------------------------------------------|--------------------------------------------------|
| region                | object  | Geographic region or market.                                        | data/processed/metrics/bev_phev_market_share.csv|
| year                  | int64   | Calendar year.                                                      | data/processed/metrics/bev_phev_market_share.csv|
| category              | object  | Data category (e.g., sales).                                        | data/processed/metrics/bev_phev_market_share.csv|
| mode                  | object  | Transport mode.                                                     | data/processed/metrics/bev_phev_market_share.csv|
| bev_sales             | float64 | Number of BEV units sold.                                           | data/processed/metrics/bev_phev_market_share.csv|
| phev_sales            | float64 | Number of PHEV units sold.                                          | data/processed/metrics/bev_phev_market_share.csv|
| bev_market_share_pct  | float64 | BEV share of total EV sales (percentage).                           | data/processed/metrics/bev_phev_market_share.csv|
| phev_market_share_pct | float64 | PHEV share of total EV sales (percentage).                          | data/processed/metrics/bev_phev_market_share.csv|

---

## Dataset: `data/processed/metrics/dashboard_summary.csv`

Pre-computed summary statistics used for dashboard KPI cards.

| Field  | Type    | Description                                       | Source file                                   |
|--------|---------|---------------------------------------------------|-----------------------------------------------|
| metric | object  | Name of the KPI metric (e.g., total_ev_stock).   | data/processed/metrics/dashboard_summary.csv  |
| value  | object  | String or numeric representation of the KPI value.| data/processed/metrics/dashboard_summary.csv  |

---

## Dataset: `data/processed/metrics/infrastructure_adequacy.csv`

Infrastructure adequacy metrics summarizing EV coverage by charging stations.

| Field                  | Type    | Description                                                                    | Source file                                        |
|------------------------|---------|--------------------------------------------------------------------------------|----------------------------------------------------|
| region                 | object  | Geographic region or market.                                                  | data/processed/metrics/infrastructure_adequacy.csv |
| year                   | object  | Year string for the metric (may be stored as text).                           | data/processed/metrics/infrastructure_adequacy.csv |
| category               | object  | Data category (e.g., infrastructure).                                         | data/processed/metrics/infrastructure_adequacy.csv |
| mode                   | object  | Transport mode.                                                               | data/processed/metrics/infrastructure_adequacy.csv |
| ev_stock               | object  | EV stock used in the adequacy calculation (string or numeric encoded).       | data/processed/metrics/infrastructure_adequacy.csv |
| total_stations         | object  | Total charging stations used in the adequacy calculation.                    | data/processed/metrics/infrastructure_adequacy.csv |
| stations_per_1000_evs  | object  | Number of stations per 1,000 EVs.                                            | data/processed/metrics/infrastructure_adequacy.csv |
| stations_per_million_evs| object | Number of stations per 1,000,000 EVs.                                        | data/processed/metrics/infrastructure_adequacy.csv |
| fast_charger_ratio     | object  | Share of stations that are fast chargers.                                    | data/processed/metrics/infrastructure_adequacy.csv |
| always_available_ratio | object  | Share of stations marked as always available.                                | data/processed/metrics/infrastructure_adequacy.csv |
| infrastructure_score   | object  | Composite infrastructure adequacy score.                                     | data/processed/metrics/infrastructure_adequacy.csv |
| adequacy_category      | object  | Categorical label for adequacy (e.g., Well Served, Adequate, Strained).     | data/processed/metrics/infrastructure_adequacy.csv |

---

## Dataset: `data/processed/metrics/regional_charging_costs.csv`

Charging cost statistics derived from station-level pricing data.

| Field                       | Type    | Description                                                         | Source file                                         |
|-----------------------------|---------|---------------------------------------------------------------------|-----------------------------------------------------|
| country                     | object  | Country name for which costs are aggregated.                        | data/processed/metrics/regional_charging_costs.csv |
| avg_cost_per_full_charge    | float64 | Average cost to fully charge a representative EV battery.           | data/processed/metrics/regional_charging_costs.csv |
| median_cost_per_full_charge | float64 | Median cost to fully charge.                                       | data/processed/metrics/regional_charging_costs.csv |
| std_cost_per_full_charge    | float64 | Standard deviation of full-charge costs.                           | data/processed/metrics/regional_charging_costs.csv |
| min_cost_per_full_charge    | float64 | Minimum observed full-charge cost.                                 | data/processed/metrics/regional_charging_costs.csv |
| max_cost_per_full_charge    | float64 | Maximum observed full-charge cost.                                 | data/processed/metrics/regional_charging_costs.csv |
| avg_cost_per_kwh            | float64 | Average cost per kWh.                                              | data/processed/metrics/regional_charging_costs.csv |
| median_cost_per_kwh         | float64 | Median cost per kWh.                                               | data/processed/metrics/regional_charging_costs.csv |
| num_stations                | int64   | Number of stations contributing to the cost statistics.            | data/processed/metrics/regional_charging_costs.csv |

---

## Dataset: `data/processed/metrics/regional_leaders.csv`

Top regions by EV adoption and infrastructure.

| Field          | Type    | Description                                              | Source file                                  |
|----------------|---------|----------------------------------------------------------|----------------------------------------------|
| region         | object  | Geographic region or market.                            | data/processed/metrics/regional_leaders.csv |
| ev_stock       | float64 | Total EV stock in the region.                          | data/processed/metrics/regional_leaders.csv |
| ev_sales       | float64 | Annual EV sales in the region.                         | data/processed/metrics/regional_leaders.csv |
| ev_sales_share | float64 | EV sales share in total vehicle sales.                 | data/processed/metrics/regional_leaders.csv |
| total_stations | float64 | Number of charging stations in the region.             | data/processed/metrics/regional_leaders.csv |

---

## Dataset: `data/processed/metrics/stations_per_ev_ratio.csv`

Stations-to-EV ratio metrics by region and year.

| Field                  | Type    | Description                                                         | Source file                                      |
|------------------------|---------|---------------------------------------------------------------------|--------------------------------------------------|
| region                 | object  | Geographic region or market.                                       | data/processed/metrics/stations_per_ev_ratio.csv|
| year                   | object  | Year string for the metric.                                        | data/processed/metrics/stations_per_ev_ratio.csv|
| category               | object  | Data category (e.g., infrastructure).                              | data/processed/metrics/stations_per_ev_ratio.csv|
| mode                   | object  | Transport mode.                                                    | data/processed/metrics/stations_per_ev_ratio.csv|
| ev_stock               | object  | EV stock used for ratio computation.                               | data/processed/metrics/stations_per_ev_ratio.csv|
| total_stations         | object  | Total charging stations used for ratio computation.                | data/processed/metrics/stations_per_ev_ratio.csv|
| stations_per_1000_evs  | object  | Number of stations per 1,000 EVs.                                  | data/processed/metrics/stations_per_ev_ratio.csv|
| stations_per_million_evs| object | Number of stations per 1,000,000 EVs.                              | data/processed/metrics/stations_per_ev_ratio.csv|
| fast_charger_ratio     | object  | Share of stations that are fast chargers.                          | data/processed/metrics/stations_per_ev_ratio.csv|
| always_available_ratio | object  | Share of stations marked as always available.                      | data/processed/metrics/stations_per_ev_ratio.csv|

---

## Dataset: `data/processed/metrics/yoy_growth_rates.csv`

Year-over-year growth rates for EV sales, stock, and charging stations.

| Field                     | Type    | Description                                                     | Source file                                 |
|---------------------------|---------|-----------------------------------------------------------------|---------------------------------------------|
| region                    | object  | Geographic region or market.                                   | data/processed/metrics/yoy_growth_rates.csv|
| year                      | int64   | Year for which growth is reported.                             | data/processed/metrics/yoy_growth_rates.csv|
| category                  | object  | Data category (e.g., sales, stock, infrastructure).            | data/processed/metrics/yoy_growth_rates.csv|
| mode                      | object  | Transport mode.                                                | data/processed/metrics/yoy_growth_rates.csv|
| powertrain                | object  | Vehicle powertrain type.                                       | data/processed/metrics/yoy_growth_rates.csv|
| ev_sales                  | float64 | EV sales in the current year.                                  | data/processed/metrics/yoy_growth_rates.csv|
| ev_sales_yoy_growth       | float64 | Year-over-year growth rate of EV sales (fraction or percent).  | data/processed/metrics/yoy_growth_rates.csv|
| ev_stock                  | float64 | EV stock in the current year.                                  | data/processed/metrics/yoy_growth_rates.csv|
| ev_stock_yoy_growth       | float64 | Year-over-year growth rate of EV stock.                        | data/processed/metrics/yoy_growth_rates.csv|
| total_stations            | float64 | Number of charging stations in the current year.               | data/processed/metrics/yoy_growth_rates.csv|
| total_stations_yoy_growth | float64 | Year-over-year growth rate of charging stations.               | data/processed/metrics/yoy_growth_rates.csv|

---

## Dataset: `data/processed/year_2024_processed/Year_2024_filled_data.csv`

Subset of IEA data for 2024 with filled values and fill metadata.

| Field       | Type    | Description                                                                 | Source file                                                    |
|------------|---------|-----------------------------------------------------------------------------|----------------------------------------------------------------|
| region     | object  | Geographic region or market.                                               | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| category   | object  | High-level data category.                                                  | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| parameter  | object  | Specific metric within the category.                                       | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| mode       | object  | Transport mode.                                                            | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| powertrain | object  | Vehicle powertrain type.                                                   | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| unit       | object  | Unit of measurement for `value`.                                           | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| value      | float64 | Filled numeric value for 2024.                                            | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| fill_method| object  | Fill method applied to this record.                                        | data/processed/year_2024_processed/Year_2024_filled_data.csv  |
| year       | int64   | Year (should be 2024 for most records).                                   | data/processed/year_2024_processed/Year_2024_filled_data.csv  |

---

## Dataset: `data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv`

Metadata for 2024 gap filling via interpolation (Method 1).

| Field                   | Type    | Description                                                           | Source file                                                       |
|-------------------------|---------|-----------------------------------------------------------------------|-------------------------------------------------------------------|
| region                  | object  | Geographic region or market.                                         | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| category                | object  | High-level data category.                                            | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| parameter               | object  | Specific metric within the category.                                 | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| mode                    | object  | Transport mode.                                                      | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| powertrain              | object  | Vehicle powertrain type.                                             | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| unit                    | object  | Unit of measurement.                                                 | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| value_2023              | float64 | Value in 2023 used for interpolation.                                | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| value_2024              | float64 | Interpolated (filled) value for 2024.                                | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| value_2025              | float64 | Forward interpolation value for 2025 (if computed).                  | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| fill_method             | object  | Label of the interpolation method used.                              | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| growth_2023_2024_pct    | float64 | Percentage growth from 2023 to 2024.                                 | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| growth_2024_2025_pct    | float64 | Percentage growth from 2024 to 2025.                                 | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |
| note                    | object  | Free-text note about the interpolation or any special handling.      | data/processed/year_2024_processed/Method1_Interpolation_Metadata.csv |

---

## Dataset: `data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv`

Metadata for 2024 gap filling via capped growth / forward-fill (Method 2).

| Field                      | Type    | Description                                                               | Source file                                                       |
|----------------------------|---------|---------------------------------------------------------------------------|-------------------------------------------------------------------|
| region                     | object  | Geographic region or market.                                             | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| category                   | object  | High-level data category.                                                | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| parameter                  | object  | Specific metric within the category.                                     | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| mode                       | object  | Transport mode.                                                          | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| powertrain                 | object  | Vehicle powertrain type.                                                 | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| unit                       | object  | Unit of measurement.                                                     | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| value_2022                 | float64 | Value in 2022 used to compute growth.                                   | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| value_2023                 | float64 | Value in 2023 used to compute growth.                                   | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| value_2024                 | float64 | Filled value for 2024 using forward-fill or capped growth.              | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| growth_rate                | float64 | Growth rate applied for forward-fill.                                   | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| threshold                  | float64 | Threshold used to cap extreme growth rates.                             | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| is_small_base              | bool    | Indicates if the base value is small (flag for sensitivity).            | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| growth_rate_uncapped       | float64 | Raw (uncapped) growth rate before applying thresholds.                  | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| fill_method                | object  | Label of the forward-fill method used.                                  | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| growth_2022_2023_pct       | float64 | Percentage growth from 2022 to 2023.                                    | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| applied_growth_rate_pct    | float64 | Growth rate actually applied after capping.                             | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| uncapped_growth_rate_pct   | float64 | Uncapped growth rate expressed as a percentage.                         | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| was_capped                 | bool    | Flag indicating if the growth rate was capped.                          | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |
| note                       | object  | Free-text note about the forward-fill decision or edge cases.          | data/processed/year_2024_processed/Method2_ForwardFill_Metadata.csv |

---

## Dataset: `data/processed/year_2024_processed/Processing_Summary_by_Region.csv`

Summary of how many records were processed by each fill method per region.

| Field              | Type    | Description                                          | Source file                                                       |
|--------------------|---------|------------------------------------------------------|-------------------------------------------------------------------|
| region             | object  | Geographic region or market.                        | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |
| method1_records    | int64   | Number of records processed using Method 1.         | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |
| method1_avg_growth | float64 | Average growth rate under Method 1.                 | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |
| method2_records    | int64   | Number of records processed using Method 2.         | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |
| method2_avg_growth | float64 | Average growth rate under Method 2.                 | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |
| total_records      | int64   | Total number of records considered for the region.  | data/processed/year_2024_processed/Processing_Summary_by_Region.csv |


