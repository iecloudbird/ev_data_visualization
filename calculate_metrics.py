import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
METRICS_DIR = PROCESSED_DIR / 'metrics'
METRICS_DIR.mkdir(exist_ok=True)

merged_df = pd.read_csv(PROCESSED_DIR / 'merged_dataset.csv')

iea_full = pd.read_csv(PROCESSED_DIR / 'IEA_Global_EV_Data_2024_filled.csv')

stations_df = pd.read_csv(PROCESSED_DIR / 'stations_enhanced.csv')
ev_stock_agg = merged_df[
    merged_df['powertrain'].isin(['BEV', 'PHEV'])
].groupby(['region', 'year', 'category', 'mode']).agg({
    'ev_stock': 'sum',
    'total_stations': 'first',
    'fast_charger_ratio': 'first',
    'always_available_ratio': 'first',
    'stations_per_million_evs': 'first'
}).reset_index()

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

if 'cost_per_full_charge' not in stations_df.columns:
    stations_df['cost_per_full_charge'] = stations_df['Cost (USD/kWh)'] * 60

cost_data = stations_df.dropna(subset=['country', 'cost_per_full_charge']).copy()

regional_costs = cost_data.groupby('country').agg({
    'cost_per_full_charge': ['mean', 'median', 'std', 'min', 'max'],
    'Cost (USD/kWh)': ['mean', 'median'],
    'Station ID': 'count'
}).reset_index()

regional_costs.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                          for col in regional_costs.columns.values]

regional_costs = regional_costs.rename(columns={
    'country': 'country',
    'cost_per_full_charge_mean': 'avg_cost_per_full_charge',
    'cost_per_full_charge_median': 'median_cost_per_full_charge',
    'cost_per_full_charge_std': 'std_cost_per_full_charge',
    'cost_per_full_charge_min': 'min_cost_per_full_charge',
    'cost_per_full_charge_max': 'max_cost_per_full_charge',
    'Cost (USD/kWh)_mean': 'avg_cost_per_kwh',
    'Cost (USD/kWh)_median': 'median_cost_per_kwh',
    'Station ID_count': 'num_stations'
})

regional_costs = regional_costs.sort_values('avg_cost_per_full_charge')

latest_year = merged_df['year'].max()
latest_data = merged_df[
    (merged_df['year'] == latest_year) &
    (merged_df['powertrain'].isin(['BEV', 'PHEV'])) &
    (merged_df['mode'] == 'Cars')
].groupby('region').agg({
    'ev_stock': 'sum',
    'ev_sales': 'sum',
    'ev_sales_share': 'first',
    'total_stations': 'first',
    'fast_charger_ratio': 'first'
}).reset_index()

world_data = latest_data[latest_data['region'] == 'World'].iloc[0]

global_summary = {
    'metric': [
        'Total EV Stock (Global)',
        'Total Charging Stations (Global)',
        'EV Sales Share (Global)',
        'Fast Charger Ratio (Global)',
    ],
    'value': [
        f"{world_data['ev_stock']:,.0f}",
        f"{world_data['total_stations']:,.0f}",
        f"{world_data['ev_sales_share']:.2f}%",
        f"{world_data['fast_charger_ratio']*100:.1f}%" if pd.notna(world_data['fast_charger_ratio']) else 'N/A',
    ],
    'year': [latest_year] * 4
}

global_summary_df = pd.DataFrame(global_summary)

regional_leaders = latest_data[
    ~latest_data['region'].isin(['World', 'Europe', 'Rest of the world', 'EU27'])
].nlargest(10, 'ev_stock')[[
    'region', 'ev_stock', 'ev_sales', 'ev_sales_share', 'total_stations'
]]

recent_years = [2021, 2022, 2023]
world_growth = growth_metrics[
    (growth_metrics['region'] == 'World') &
    (growth_metrics['mode'] == 'Cars') &
    (growth_metrics['year'].isin(recent_years))
]

avg_growth_summary = {
    'metric': [
        'Avg YoY EV Sales Growth (2021-2023)',
        'Avg YoY EV Stock Growth (2021-2023)',
        'Avg YoY Stations Growth (2021-2023)'
    ],
    'value': [
        f"{world_growth['ev_sales_yoy_growth'].mean():.1f}%",
        f"{world_growth['ev_stock_yoy_growth'].mean():.1f}%",
        f"{world_growth['total_stations_yoy_growth'].mean():.1f}%"
    ]
}

avg_growth_df = pd.DataFrame(avg_growth_summary)

dashboard_summary = pd.concat([
    global_summary_df[['metric', 'value']],
    avg_growth_df
], ignore_index=True)

output_files = {
    'stations_per_ev_ratio.csv': stations_ratio,
    'yoy_growth_rates.csv': growth_metrics,
    'infrastructure_adequacy.csv': infrastructure_adequacy,
    'bev_phev_market_share.csv': market_share_pivot,
    'regional_charging_costs.csv': regional_costs,
    'dashboard_summary.csv': dashboard_summary,
    'regional_leaders.csv': regional_leaders
}

for filename, dataframe in output_files.items():
    filepath = METRICS_DIR / filename
    dataframe.to_csv(filepath, index=False)
