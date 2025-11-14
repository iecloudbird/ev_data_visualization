# Global EV Charging Stations Merged Dataset

**File:** `ev_stations_merged_global.csv`  
**Generated:** November 14, 2025

## Overview

This dataset combines international EV charging station data with Chinese charging station data from CnOpenData, creating a comprehensive global database of EV charging infrastructure.

## Dataset Statistics

- **Total stations:** 12,002
- **Countries covered:** 72
- **Unique operators:** 264
- **Data sources:**
  - International: 10,000 stations (83.3%) from `ev_stations_2025.csv`
  - Chinese: 2,002 stations (16.7%) from `CnOpenData全国充电站分布数据（样本数据）.xlsx`

## Top 10 Countries by Station Count

| Country            | Stations  | Percentage |
| ------------------ | --------- | ---------- |
| Canada (CA)        | 4,135     | 34.5%      |
| United States (US) | 2,266     | 18.9%      |
| **China (CN)**     | **2,003** | **16.7%**  |
| Spain (ES)         | 888       | 7.4%       |
| Russia (RU)        | 392       | 3.3%       |
| Turkey (TR)        | 377       | 3.1%       |
| Malaysia (MY)      | 377       | 3.1%       |
| Denmark (DK)       | 296       | 2.5%       |
| Brazil (BR)        | 199       | 1.7%       |
| Italy (IT)         | 134       | 1.1%       |

## Schema

The merged dataset follows the international station format:

| Column            | Description               | Example                                          |
| ----------------- | ------------------------- | ------------------------------------------------ |
| `id`              | Unique station identifier | 500000                                           |
| `title`           | Station name              | "比亚迪电动汽车充电站" (BYD EV Charging Station) |
| `address`         | Street address            | "府前街 1 号万达广场地下一层"                    |
| `town`            | District/town             | "通州区" (Tongzhou District)                     |
| `state`           | Province/state            | "Beijing"                                        |
| `postcode`        | Postal code               | "101100"                                         |
| `country`         | ISO country code          | "CN"                                             |
| `lat`             | Latitude                  | 39.909177                                        |
| `lon`             | Longitude                 | 116.663764                                       |
| `operator`        | Station operator          | "(Unknown Operator)"                             |
| `status`          | Operational status        | "Operational"                                    |
| `num_connectors`  | Number of connectors      | 1                                                |
| `connector_types` | Connector types available | "Type 2 (Socket Only)"                           |
| `date_added`      | Date added to database    | "2025-11-14 00:01:42+00:00"                      |

## Chinese Data Processing

### Translation Applied

1. **Column Names:** All Chinese column headers translated to English
2. **Province Names:** Chinese provinces translated using standardized names
   - Original: `台湾省`, `北京市`, `广东省`
   - Translated: `Taiwan`, `Beijing`, `Guangdong`

### Mapping Details

Chinese dataset columns were mapped to the international schema:

- **地点名称** (Location Name) → `title`
- **详细地址** (Detailed Address) → `address`
- **区域名称** (District Name) → `town`
- **省份名称** (Province Name) → `state` (translated)
- **邮政编码** (Postcode) → `postcode`
- **经度/纬度** (Longitude/Latitude) → `lon`/`lat`
- **商业类型** (Business Type) → `operator`

### Default Values for Chinese Stations

- `country`: "CN"
- `status`: "Operational"
- `num_connectors`: 1 (conservative estimate)
- `connector_types`: "Type 2 (Socket Only)" (common in China)
- `date_added`: Import timestamp (2025-11-14)

## Data Quality

- **Missing coordinates:** 2 records (0.02%)
- **Duplicate IDs:** 0 records
- **Invalid coordinates:** 0 records

## Status Distribution

| Status                  | Count  | Percentage |
| ----------------------- | ------ | ---------- |
| Operational             | 11,303 | 94.2%      |
| Planned For Future Date | 302    | 2.5%       |
| Temporarily Unavailable | 176    | 1.5%       |
| Not Operational         | 136    | 1.1%       |
| Unknown                 | 80     | 0.7%       |
| Partly Operational      | 5      | 0.0%       |

## Top 10 Operators

1. (Unknown Operator) - 2,425 stations
2. Circuit Electrique - 1,979 stations
3. ChargePoint - 1,275 stations
4. flo - 724 stations
5. PowerGo - 421 stations
6. Punkt-E - 366 stations
7. ChargeSini - 363 stations
8. Red E Charge - 278 stations
9. Blink Charging - 245 stations
10. (Business Owner at Location) - 243 stations

## Usage Notes

### Connector Types

Chinese station connector types are set to "Type 2 (Socket Only)" as a default. In reality, many Chinese stations may use:

- GB/T AC (Chinese standard for AC charging)
- GB/T DC (Chinese standard for DC fast charging)
- CHAdeMO (common in older stations)
- CCS (newer installations)

Users should verify connector compatibility when using Chinese station data for trip planning.

### Province Names

Chinese provinces are stored with English names for consistency:

- `Beijing`, `Shanghai`, `Guangdong`, `Zhejiang`, etc.
- Special regions: `Hong Kong`, `Macau`, `Taiwan`

### Data Freshness

- **International data:** Current as of dataset date (2025-11-02)
- **Chinese data:** Sample dataset (representative, not exhaustive)
- **Import date:** 2025-11-14

## Files Generated

1. **`ev_stations_merged_global.csv`** - Main merged dataset (2.16 MB)
2. **`sample_chinese_stations.csv`** - 10 sample Chinese stations for verification
3. **`sample_international_stations.csv`** - 10 sample international stations for verification

## Processing Notebook

The merge was performed using: `notebooks/merge_ev_stations.ipynb`

This notebook includes:

- Chinese-to-English translation dictionaries
- Column mapping logic
- Data quality checks
- Verification samples

## Known Limitations

1. **Chinese Station Coverage:** The Chinese dataset is a sample (2,002 stations) and does not represent complete national coverage
2. **Connector Information:** Chinese stations use default values for connector types and counts
3. **Operator Information:** Many Chinese stations have "(Unknown Operator)" as the operator
4. **Province Translation:** Some regions may retain Chinese characters if not in the translation dictionary

## Future Enhancements

Potential improvements for future versions:

- Expand Chinese province translation dictionary
- Add GB/T connector type to Chinese stations
- Integrate real-time status updates
- Add pricing information for Chinese stations
- Include charging power/speed information

## Citation

When using this dataset, please cite both sources:

- International data: Open Charge Map / EV Stations 2025
- Chinese data: CnOpenData (全国充电站分布数据样本数据)

---
