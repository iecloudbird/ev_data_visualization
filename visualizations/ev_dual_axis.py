"""
EV Dual-Axis Visualization
===========================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_prepare_data():
    df = pd.read_csv(DATA_DIR / 'merged_dataset.csv')
    ev_data = df[
        (df['mode'] == 'Cars') & 
        (df['powertrain'].isin(['BEV', 'PHEV']))
    ].copy()
    agg_data = ev_data.groupby(['region', 'year']).agg({
        'ev_stock': 'sum',
        'ev_sales': 'sum',
        'ev_sales_share': 'first'
    }).reset_index()
    charging_data = df[
        (df['mode'] == 'EV') & 
        (df['powertrain'].str.contains('Publicly available', na=False))
    ].copy()
    charging_agg = charging_data.groupby(['region', 'year']).agg({
        'ev_charging_points': 'sum'
    }).reset_index()
    charging_agg.rename(columns={'ev_charging_points': 'total_stations'}, inplace=True)
    merged = agg_data.merge(charging_agg, on=['region', 'year'], how='left')
    merged = merged.sort_values(['region', 'year'])
    merged['ev_stock_growth'] = merged.groupby('region')['ev_stock'].pct_change() * 100
    merged['ev_sales_growth'] = merged.groupby('region')['ev_sales'].pct_change() * 100
    return merged


def get_top_regions(data, n=10, metric='ev_stock', exclude_aggregates=True):
    latest_year = data['year'].max()
    latest_data = data[data['year'] == latest_year].copy()
    if exclude_aggregates:
        exclude_list = ['World', 'Europe', 'EU27', 'Rest of the world']
        latest_data = latest_data[~latest_data['region'].isin(exclude_list)]
    top_regions = latest_data.nlargest(n, metric)['region'].tolist()
    return top_regions


def calculate_trend_projection(x, y, future_years=3):
    mask = ~np.isnan(y)
    x_clean = x[mask]
    y_clean = y[mask]
    if len(x_clean) < 2:
        return None, None, None
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    x_extended = np.arange(x_clean.min(), x_clean.max() + future_years + 1)
    y_trend = slope * x_extended + intercept
    return x_extended, y_trend, r_value**2


def create_dual_axis_chart(
    regions=None,
    metric='EV Stock',
    log_scale=False,
    year_range=None,
    show_projections=True,
    output_file='ev_dual_axis_chart.png',
    figsize=(16, 10)
):
    data = load_and_prepare_data()
    if year_range:
        data = data[(data['year'] >= year_range[0]) & (data['year'] <= year_range[1])]
    if regions is None:
        regions = get_top_regions(data, n=10)
    plot_data = data[data['region'].isin(regions)].copy()
    metric_map = {
        'EV Stock': 'ev_stock',
        'EV Sales': 'ev_sales',
        'Growth Rate %': 'ev_stock_growth'
    }
    metric_col = metric_map.get(metric, 'ev_stock')
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    colors = plt.cm.tab10(np.linspace(0, 1, len(regions)))
    for idx, region in enumerate(regions):
        region_data = plot_data[plot_data['region'] == region].sort_values('year')
        if len(region_data) == 0:
            continue
        years = region_data['year'].values
        values = region_data[metric_col].values
        ax1.plot(years, values, marker='o', linewidth=2.5, 
                label=region, color=colors[idx], markersize=6, alpha=0.8)
        if show_projections and metric != 'Growth Rate %':
            x_proj, y_proj, r2 = calculate_trend_projection(years, values, future_years=3)
            if x_proj is not None:
                proj_years = x_proj[x_proj > years.max()]
                proj_values = y_proj[x_proj > years.max()]
                ax1.plot(proj_years, proj_values, linestyle='--', 
                        linewidth=1.5, color=colors[idx], alpha=0.5)
    charging_totals = plot_data.groupby('year')['total_stations'].sum().reset_index()
    if len(charging_totals) > 0:
        ax2.fill_between(charging_totals['year'], 0, charging_totals['total_stations'],
                         alpha=0.25, color='gray', label='Total Charging Stations')
        ax2.plot(charging_totals['year'], charging_totals['total_stations'],
                color='gray', linewidth=2, alpha=0.6)
    year_min = plot_data['year'].min()
    year_max = plot_data['year'].max()
    
    # Set log scale first if needed (affects ylim)
    if log_scale:
        ax1.set_yscale('log')
        ax2.set_yscale('log')
    
    # Get y-axis limits after log scale is set
    y_min, y_max = ax1.get_ylim()
    
    # Determine annotation positions based on chart type
    if log_scale or 'log' in output_file:
        # Log scale: all at bottom (use logarithmic positioning)
        # Position at ~10% from bottom in log space
        log_ratio = (y_max / y_min) ** 0.1
        paris_y = y_min * log_ratio
        eu_y = y_min * log_ratio
        us_y = y_min * log_ratio
    elif 'recent' in output_file:
        # Top5, sales, recent: Paris in middle, others at top
        paris_y = y_min + (y_max - y_min) * 0.5
        eu_y = y_max * 0.95
        us_y = y_max * 0.95
    else:
        # Normal chart: all at same height (top)
        paris_y = y_max * 0.95
        eu_y = y_max * 0.95
        us_y = y_max * 0.95
    
    if year_min <= 2016 <= year_max:
        ax1.axvline(x=2016, color='red', linestyle=':', linewidth=2, alpha=0.6)
        ax1.text(2016, paris_y, 'Paris Agreement\n(2016)', 
                ha='center', va='top', fontsize=10, color='red',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    if year_min <= 2020 <= year_max:
        ax1.axvline(x=2020, color='green', linestyle=':', linewidth=2, alpha=0.6)
        ax1.text(2020, eu_y, 'EU Green Deal\n(2020)', 
                ha='center', va='top', fontsize=10, color='green',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    if year_min <= 2022 <= year_max:
        ax1.axvline(x=2022, color='blue', linestyle='--', linewidth=2, alpha=0.7)
        ax1.text(2022, us_y, 'U.S. Federal\nEV Tax Credit\nExpansion (2022)',
                ha='center', va='top', fontsize=10, color='blue',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85))
    ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax1.set_ylabel(metric, fontsize=14, fontweight='bold', color='black')
    ax2.set_ylabel('Total Charging Stations', fontsize=14, fontweight='bold', color='gray')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=11)
    ax2.tick_params(axis='y', labelcolor='gray', labelsize=11)
    ax1.tick_params(axis='x', labelsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    title = f'EV {metric} and Charging Infrastructure Trends'
    if year_range:
        title += f' ({year_range[0]}-{year_range[1]})'
    plt.title(title, fontsize=18, fontweight='bold', pad=20)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc='upper left', fontsize=10, 
              framealpha=0.9, title='Regions', title_fontsize=11)
    ax2.legend(lines2, labels2, loc='upper right', fontsize=10, framealpha=0.9)
    if not log_scale:
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    plt.tight_layout()
    output_path = OUTPUT_DIR / output_file
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    return fig, ax1, ax2


def main():
    fig, ax1, ax2 = create_dual_axis_chart(
        regions=None,
        metric='EV Stock',
        log_scale=False,
        year_range=None,
        show_projections=True,
        output_file='ev_dual_axis_chart.png'
    )
    create_dual_axis_chart(
        regions=None,
        metric='EV Stock',
        log_scale=True,
        output_file='ev_dual_axis_chart_log.png'
    )
    create_dual_axis_chart(
        regions=None,
        metric='EV Sales',
        log_scale=False,
        output_file='ev_dual_axis_chart_sales.png'
    )
    create_dual_axis_chart(
        regions=None,
        metric='EV Stock',
        log_scale=False,
        year_range=(2015, 2023),
        output_file='ev_dual_axis_chart_recent.png'
    )
    data = load_and_prepare_data()
    top_5 = get_top_regions(data, n=5)
    create_dual_axis_chart(
        regions=top_5,
        metric='EV Stock',
        log_scale=False,
        output_file='ev_dual_axis_chart_top5.png'
    )
    print("All charts created successfully!")


if __name__ == '__main__':
    main()

