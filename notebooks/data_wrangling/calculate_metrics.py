import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
METRICS_DIR = PROCESSED_DIR / 'metrics'
METRICS_DIR.mkdir(exist_ok=True)

merged_df = pd.read_csv(PROCESSED_DIR / 'merged_dataset.csv')

iea_full = pd.read_csv(PROCESSED_DIR / 'IEA_Global_EV_Data_2024_filled.csv')

# Load merged global stations dataset
stations_df = pd.read_csv(PROCESSED_DIR / 'merged_charging_station' / 'ev_stations_merged_global.csv')

# Aggregate station count per country
station_country_agg = stations_df.groupby('country').agg({
    'id': 'count',
    'operator': lambda x: x.nunique(),
    'status': lambda x: (x == 'Operational').mean(),
    'num_connectors': 'mean'
}).rename(columns={
    'id': 'total_stations',
    'operator': 'unique_operators',
    'status': 'operational_ratio',
    'num_connectors': 'avg_connectors'
}).reset_index()

ev_stock_agg = merged_df[
    merged_df['powertrain'].isin(['BEV', 'PHEV'])
].groupby(['region', 'year', 'category', 'mode']).agg({
    'ev_stock': 'sum',
    'total_stations': 'first',
    'stations_per_million_evs': 'first'
}).reset_index()

# Add missing columns as NaN for compatibility
for col in ['fast_charger_ratio', 'always_available_ratio']:
    ev_stock_agg[col] = np.nan

ev_stock_agg['stations_per_1000_evs'] = np.where(
    ev_stock_agg['ev_stock'] > 0,
    (ev_stock_agg['total_stations'] / (ev_stock_agg['ev_stock'] / 1000)),
    np.nan
)

stations_ratio = ev_stock_agg[[
    'region', 'year', 'category', 'mode',
    'ev_stock', 'total_stations',
    'stations_per_1000_evs', 'stations_per_million_evs',
    'fast_charger_ratio', 'always_available_ratio'
]].copy()

stations_ratio = stations_ratio.dropna(subset=['ev_stock', 'total_stations'])
growth_base = merged_df[
    merged_df['powertrain'].isin(['BEV', 'PHEV'])
].groupby(['region', 'mode', 'year']).agg({
    'ev_sales': 'sum',
    'ev_stock': 'sum',
    'total_stations': 'first',
    'category': 'first'
}).reset_index()

growth_base = growth_base.sort_values(['region', 'mode', 'year'])

def calculate_growth_rate(group):
    group['ev_sales_yoy_growth'] = group['ev_sales'].pct_change() * 100
    group['ev_stock_yoy_growth'] = group['ev_stock'].pct_change() * 100
    group['total_stations_yoy_growth'] = group['total_stations'].pct_change() * 100
    return group

growth_metrics = growth_base.groupby(['region', 'mode'], group_keys=False).apply(calculate_growth_rate)

growth_metrics['powertrain'] = 'EV'
growth_metrics = growth_metrics[[
    'region', 'year', 'category', 'mode', 'powertrain',
    'ev_sales', 'ev_sales_yoy_growth',
    'ev_stock', 'ev_stock_yoy_growth',
    'total_stations', 'total_stations_yoy_growth'
]].copy()

growth_metrics = growth_metrics.replace([np.inf, -np.inf], np.nan)

def calculate_infrastructure_score(row):
    stations_score = min(row['stations_per_1000_evs'] / 10 * 100, 100) if pd.notna(row['stations_per_1000_evs']) else 0
    fast_charger_score = row['fast_charger_ratio'] * 100 if pd.notna(row['fast_charger_ratio']) else 0
    availability_score = row['always_available_ratio'] * 100 if pd.notna(row['always_available_ratio']) else 0
    total_score = (stations_score * 0.5) + (fast_charger_score * 0.25) + (availability_score * 0.25)
    return total_score

infrastructure_adequacy = stations_ratio.copy()
infrastructure_adequacy['infrastructure_score'] = infrastructure_adequacy.apply(
    calculate_infrastructure_score, axis=1
)

score_percentiles = infrastructure_adequacy['infrastructure_score'].quantile([0.33, 0.67])

def categorize_adequacy(score):
    if pd.isna(score):
        return 'Unknown'
    elif score >= score_percentiles[0.67]:
        return 'Well-served'
    elif score >= score_percentiles[0.33]:
        return 'Strained'
    else:
        return 'Insufficient'

infrastructure_adequacy['adequacy_category'] = infrastructure_adequacy['infrastructure_score'].apply(
    categorize_adequacy
)

powertrain_data = merged_df[
    merged_df['powertrain'].isin(['BEV', 'PHEV'])
].copy()

total_ev_sales = powertrain_data.groupby(
    ['region', 'year', 'category', 'mode']
)['ev_sales'].sum().reset_index(name='total_ev_sales')

powertrain_shares = powertrain_data.merge(
    total_ev_sales,
    on=['region', 'year', 'category', 'mode'],
    how='left'
)

powertrain_shares['market_share_pct'] = np.where(
    powertrain_shares['total_ev_sales'] > 0,
    (powertrain_shares['ev_sales'] / powertrain_shares['total_ev_sales']) * 100,
    np.nan
)

market_share_pivot = powertrain_shares.pivot_table(
    index=['region', 'year', 'category', 'mode'],
    columns='powertrain',
    values=['ev_sales', 'market_share_pct'],
    aggfunc='first'
).reset_index()

market_share_pivot.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                                for col in market_share_pivot.columns.values]

market_share_pivot = market_share_pivot.rename(columns={
    'ev_sales_BEV': 'bev_sales',
    'ev_sales_PHEV': 'phev_sales',
    'market_share_pct_BEV': 'bev_market_share_pct',
    'market_share_pct_PHEV': 'phev_market_share_pct'
})

# ============================================================================
# INFRASTRUCTURE ADEQUACY: 2023 EV Stock vs 2025 Charging Infrastructure
# ============================================================================
# Calculate EVs per charger ratio by country to assess infrastructure adequacy
# Since station data has date_added=2025, we compare 2023 EV stock with 2025 infrastructure

# Get 2023 EV stock data by region from IEA dataset
ev_stock_2023 = iea_full[
    (iea_full['parameter'] == 'EV stock') &
    (iea_full['year'] == 2023) &
    (iea_full['mode'] == 'Cars') &
    (iea_full['category'] == 'Historical')
].copy()

# Aggregate EV stock by region (sum across all powertrains)
ev_stock_2023_agg = ev_stock_2023.groupby('region')['value'].sum().reset_index()
ev_stock_2023_agg.columns = ['region', 'ev_stock_2023']

# Map ISO country codes to IEA region names
# This mapping is needed to join station data (country codes) with IEA data (region names)
iso_to_region = {
    'CN': 'China', 'US': 'USA', 'USA': 'USA',
    'DE': 'Germany', 'DEU': 'Germany',
    'FR': 'France', 'FRA': 'France',
    'GB': 'United Kingdom', 'GBR': 'United Kingdom',
    'JP': 'Japan', 'JPN': 'Japan',
    'KR': 'Korea', 'KOR': 'Korea',
    'NO': 'Norway', 'NOR': 'Norway',
    'SE': 'Sweden', 'SWE': 'Sweden',
    'NL': 'Netherlands', 'NLD': 'Netherlands',
    'IT': 'Italy', 'ITA': 'Italy',
    'ES': 'Spain', 'ESP': 'Spain',
    'BE': 'Belgium', 'BEL': 'Belgium',
    'AT': 'Austria', 'AUT': 'Austria',
    'CH': 'Switzerland', 'CHE': 'Switzerland',
    'DK': 'Denmark', 'DNK': 'Denmark',
    'CA': 'Canada', 'CAN': 'Canada',
    'AU': 'Australia', 'AUS': 'Australia',
    'IN': 'India', 'IND': 'India',
    'BR': 'Brazil', 'BRA': 'Brazil',
    'MX': 'Mexico', 'MEX': 'Mexico',
    'FI': 'Finland', 'FIN': 'Finland',
    'PT': 'Portugal', 'PRT': 'Portugal',
    'PL': 'Poland', 'POL': 'Poland',
    'CZ': 'Czechia', 'CZE': 'Czechia',
    'GR': 'Greece', 'GRC': 'Greece',
    'TR': 'Turkiye', 'TUR': 'Turkiye',
    'NZ': 'New Zealand', 'NZL': 'New Zealand',
    'IL': 'Israel', 'ISR': 'Israel',
    'ZA': 'South Africa', 'ZAF': 'South Africa',
    'IE': 'Ireland', 'IRL': 'Ireland',
    'HU': 'Hungary', 'HUN': 'Hungary',
    'RO': 'Romania', 'ROU': 'Romania',
    'IS': 'Iceland', 'ISL': 'Iceland',
    'LU': 'Luxembourg', 'LUX': 'Luxembourg',
    'SI': 'Slovenia', 'SVN': 'Slovenia',
    'SK': 'Slovakia', 'SVK': 'Slovakia',
    'HR': 'Croatia', 'HRV': 'Croatia',
    'BG': 'Bulgaria', 'BGR': 'Bulgaria',
    'EE': 'Estonia', 'EST': 'Estonia',
    'LV': 'Latvia', 'LVA': 'Latvia',
    'LT': 'Lithuania', 'LTU': 'Lithuania',
    'ID': 'Indonesia', 'IDN': 'Indonesia',
    'MY': 'Malaysia', 'MYS': 'Malaysia',
    'SG': 'Singapore', 'SGP': 'Singapore',
    'CL': 'Chile', 'CHL': 'Chile',
    'MT': 'Malta', 'MLT': 'Malta',
    'CY': 'Cyprus', 'CYP': 'Cyprus',
    'CR': 'Costa Rica', 'CRI': 'Costa Rica'
}

# Aggregate stations by country (2025 infrastructure data)
stations_2025_agg = stations_df.groupby('country').agg({
    'id': 'count',
    'num_connectors': 'sum'  # Total connectors, not just stations
}).rename(columns={
    'id': 'total_stations_2025',
    'num_connectors': 'total_connectors_2025'
}).reset_index()

# Map country codes to regions
stations_2025_agg['region'] = stations_2025_agg['country'].map(iso_to_region)

# Remove rows where mapping failed (country code not in mapping)
stations_2025_agg = stations_2025_agg[stations_2025_agg['region'].notna()]

# Aggregate stations by region (handles multiple country codes mapping to same region,
# and automatically creates aggregates like "Europe" if individual EU countries are present)
stations_2025_by_region = stations_2025_agg.groupby('region').agg({
    'total_stations_2025': 'sum',
    'total_connectors_2025': 'sum'
}).reset_index()

# Merge EV stock 2023 with stations 2025
infrastructure_adequacy_2023_2025 = ev_stock_2023_agg.merge(
    stations_2025_by_region[['region', 'total_stations_2025', 'total_connectors_2025']],
    on='region',
    how='inner'
)

# Calculate EVs per charger ratios
# Using connectors instead of stations gives a more accurate picture
infrastructure_adequacy_2023_2025['evs_per_station'] = np.where(
    infrastructure_adequacy_2023_2025['total_stations_2025'] > 0,
    infrastructure_adequacy_2023_2025['ev_stock_2023'] / infrastructure_adequacy_2023_2025['total_stations_2025'],
    np.nan
)

infrastructure_adequacy_2023_2025['evs_per_connector'] = np.where(
    infrastructure_adequacy_2023_2025['total_connectors_2025'] > 0,
    infrastructure_adequacy_2023_2025['ev_stock_2023'] / infrastructure_adequacy_2023_2025['total_connectors_2025'],
    np.nan
)

# Calculate infrastructure deficit
# Target: ~30 EVs/Charger in USA (based on industry benchmarks)
TARGET_EVS_PER_CHARGER = 30.0

infrastructure_adequacy_2023_2025['infrastructure_deficit'] = np.where(
    infrastructure_adequacy_2023_2025['evs_per_connector'].notna(),
    infrastructure_adequacy_2023_2025['evs_per_connector'] - TARGET_EVS_PER_CHARGER,
    np.nan
)

infrastructure_adequacy_2023_2025['deficit_pct'] = np.where(
    infrastructure_adequacy_2023_2025['evs_per_connector'].notna() & (infrastructure_adequacy_2023_2025['evs_per_connector'] > 0),
    ((infrastructure_adequacy_2023_2025['evs_per_connector'] - TARGET_EVS_PER_CHARGER) / TARGET_EVS_PER_CHARGER) * 100,
    np.nan
)

# Categorize adequacy levels
def categorize_infrastructure_adequacy(evs_per_connector):
    """Categorize infrastructure adequacy based on EVs per connector ratio."""
    if pd.isna(evs_per_connector):
        return 'Unknown'
    elif evs_per_connector <= 20:
        return 'Well-served'  # Better than target
    elif evs_per_connector <= 30:
        return 'Adequate'  # At or near target
    elif evs_per_connector <= 50:
        return 'Strained'  # Moderate deficit
    else:
        return 'Insufficient'  # Significant deficit

infrastructure_adequacy_2023_2025['adequacy_category'] = infrastructure_adequacy_2023_2025['evs_per_connector'].apply(
    categorize_infrastructure_adequacy
)

# Identify major markets and their infrastructure status
major_markets = ['China', 'USA', 'Europe']
infrastructure_major_markets = infrastructure_adequacy_2023_2025[
    infrastructure_adequacy_2023_2025['region'].isin(major_markets)
].copy()

# Find the market with the highest EVs per charger ratio (worst infrastructure adequacy)
worst_market = infrastructure_adequacy_2023_2025.loc[
    infrastructure_adequacy_2023_2025['evs_per_connector'].idxmax()
] if not infrastructure_adequacy_2023_2025['evs_per_connector'].isna().all() else None

# Print summary statistics
print("\n" + "="*80)
print("📊 INFRASTRUCTURE ADEQUACY ANALYSIS (2023 EV Stock vs 2025 Infrastructure)")
print("="*80)
print(f"\nTarget Benchmark: ~{TARGET_EVS_PER_CHARGER:.0f} EVs per Charger Connector")
print(f"\nTotal countries/regions analyzed: {len(infrastructure_adequacy_2023_2025)}")

if worst_market is not None and pd.notna(worst_market['evs_per_connector']):
    print(f"\n🔴 Highest Infrastructure Deficit:")
    print(f"   Region: {worst_market['region']}")
    print(f"   EVs per Connector: {worst_market['evs_per_connector']:.1f}")
    print(f"   Deficit: {worst_market['infrastructure_deficit']:.1f} EVs/Charger")
    print(f"   Deficit %: {worst_market['deficit_pct']:.1f}% above target")

if len(infrastructure_major_markets) > 0:
    print(f"\n📈 Major Markets Infrastructure Status:")
    for _, row in infrastructure_major_markets.iterrows():
        status_emoji = "🟢" if row['adequacy_category'] in ['Well-served', 'Adequate'] else "🟡" if row['adequacy_category'] == 'Strained' else "🔴"
        print(f"\n   {status_emoji} {row['region']}:")
        print(f"      EVs per Connector: {row['evs_per_connector']:.1f}")
        print(f"      Category: {row['adequacy_category']}")
        if pd.notna(row['deficit_pct']):
            deficit_sign = "+" if row['deficit_pct'] > 0 else ""
            print(f"      Deficit: {deficit_sign}{row['deficit_pct']:.1f}% vs target")

# Sort by EVs per connector (descending) for easy identification of worst cases
# NaN values will be placed at the end by default
infrastructure_adequacy_2023_2025 = infrastructure_adequacy_2023_2025.sort_values(
    'evs_per_connector', 
    ascending=False
)

output_files = {
    'stations_per_ev_ratio.csv': stations_ratio,
    'yoy_growth_rates.csv': growth_metrics,
    'infrastructure_adequacy.csv': infrastructure_adequacy,
    'bev_phev_market_share.csv': market_share_pivot,
    'infrastructure_adequacy_2023_2025.csv': infrastructure_adequacy_2023_2025,
    'major_markets_infrastructure.csv': infrastructure_major_markets
}

for filename, dataframe in output_files.items():
    filepath = METRICS_DIR / filename
    dataframe.to_csv(filepath, index=False)
    print(f"\n✅ Saved: {filepath}")
