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

output_files = {
    'stations_per_ev_ratio.csv': stations_ratio,
    'yoy_growth_rates.csv': growth_metrics,
    'infrastructure_adequacy.csv': infrastructure_adequacy,
    'bev_phev_market_share.csv': market_share_pivot
}

for filename, dataframe in output_files.items():
    filepath = METRICS_DIR / filename
    dataframe.to_csv(filepath, index=False)
