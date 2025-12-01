# -*- coding: utf-8 -*-
"""
Modernized chart components for the EV Dashboard.
Matches finalized visualizations from ev.ipynb and ev_stations_map.ipynb.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_choropleth_map(df: pd.DataFrame, selected_year: int):
    region_to_iso = {
        'China': 'CHN', 'USA': 'USA', 'Germany': 'DEU', 'France': 'FRA',
        'United Kingdom': 'GBR', 'Japan': 'JPN', 'Korea': 'KOR', 'South Korea': 'KOR',
        'Norway': 'NOR', 'Sweden': 'SWE', 'Netherlands': 'NLD', 'Italy': 'ITA',
        'Spain': 'ESP', 'Belgium': 'BEL', 'Austria': 'AUT', 'Switzerland': 'CHE',
        'Denmark': 'DNK', 'Canada': 'CAN', 'Australia': 'AUS', 'India': 'IND',
        'Brazil': 'BRA', 'Mexico': 'MEX', 'Thailand': 'THA', 'Finland': 'FIN',
        'Portugal': 'PRT', 'Poland': 'POL', 'Czechia': 'CZE', 'Greece': 'GRC',
        'Turkey': 'TUR', 'Türkiye': 'TUR', 'Turkiye': 'TUR',
        'New Zealand': 'NZL', 'Israel': 'ISR', 'South Africa': 'ZAF',
        'Ireland': 'IRL', 'Hungary': 'HUN', 'Romania': 'ROU', 'Iceland': 'ISL',
        'Luxembourg': 'LUX', 'Slovenia': 'SVN', 'Slovakia': 'SVK', 'Croatia': 'HRV',
        'Bulgaria': 'BGR', 'Estonia': 'EST', 'Latvia': 'LVA', 'Lithuania': 'LTU',
        'Indonesia': 'IDN', 'Malaysia': 'MYS', 'Singapore': 'SGP', 'Chile': 'CHL',
        'Malta': 'MLT', 'Cyprus': 'CYP', 'Costa Rica': 'CRI'
    }
    df_latest = df[df['year'] == selected_year].copy()
    df_mapped = df_latest[df_latest['region'].isin(region_to_iso.keys())].copy()
    df_mapped['iso_code'] = df_mapped['region'].map(region_to_iso)

    fig = px.choropleth(
        df_mapped,
        locations='iso_code',
        color='total_ev_stock',
        hover_name='region',
        hover_data={'total_ev_stock': ':,.0f', 'iso_code': False},
        color_continuous_scale=[
            [0, '#F0F9FF'], [0.15, '#BAE6FD'], [0.35, '#38BDF8'],
            [0.6, '#0EA5E9'], [0.8, '#0284C7'], [1, '#0C4A6E']
        ],
        labels={'total_ev_stock': 'EV Stock'}
    )
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=True, coastlinecolor='#CCC',
            projection_type='natural earth', bgcolor='#E8E8E8', landcolor='#F5F5F5',
            oceancolor='#FFF', lakecolor='#FFF', showcountries=True,
            countrycolor='#DDD', countrywidth=0.5
        ),
        height=450,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#FFF',
        title=dict(text=f'<b>Global EV Stock Distribution ({selected_year})</b>', x=0.5),
        font=dict(family='Arial, sans-serif', size=12, color='#171A20'),
        coloraxis_colorbar=dict(title=dict(text='EV Stock\n(vehicles)', font=dict(size=11)))
    )
    return fig


def create_timeseries_chart(df: pd.DataFrame, selected_regions, show_annotations: bool = True):
    """Create a time-series chart of EV adoption trends by region with policy annotations."""
    df_filtered = df[(df['region'].isin(selected_regions)) & (df['region'] != 'World') & (df['region'] != 'EU27')].copy()
    df_filtered['region'] = df_filtered['region'].replace({"Rest of the world": "Others"})
    df_filtered = df_filtered.sort_values(['year', 'total_ev_stock'], ascending=[True, False])

    color_map = {
        'China': '#d62728', 'Europe': '#2ca02c', 'USA': '#ff7f0e',
        'Germany': '#9467bd', 'France': '#8c564b', 'United Kingdom': '#e377c2',
        'Japan': '#7f7f7f', 'Norway': '#bcbd22', 'Others': '#17becf'
    }

    fig = go.Figure()
    for region in df_filtered['region'].unique():
        df_region = df_filtered[df_filtered['region'] == region]
        fig.add_trace(go.Scatter(
            x=df_region['year'], y=df_region['total_ev_stock'], mode='lines+markers', name=region,
            line=dict(width=2.5 if region in ['China', 'USA', 'Europe'] else 1.5, color=color_map.get(region, '#888')),
            marker=dict(size=6),
            hovertemplate=f'<b>{region}</b><br>Year: %{{x}}<br>EV Stock: %{{y:,.0f}}<extra></extra>'
        ))

    # Policy annotations
    if show_annotations:
        policy_annotations = [
            dict(x=2014, y=320000, xref='x', yref='y',
                 text="🇨🇳 2014: NEV Subsidies<br><i>Central+local subsidies launch</i>",
                 showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor='#d62728', ax=-60, ay=-40,
                 bgcolor='rgba(214,39,40,0.1)', bordercolor='#d62728', font=dict(size=10)),
            dict(x=2018, y=2600000, xref='x', yref='y',
                 text="🇨🇳 2018: Tax Exemption<br><i>NEVs exempt from vehicle tax</i>",
                 showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor='#d62728', ax=-80, ay=-50,
                 bgcolor='rgba(214,39,40,0.15)', bordercolor='#d62728', font=dict(size=10)),
            dict(x=2019, y=1700000, xref='x', yref='y',
                 text="🇪🇺 2019: EU CO₂ Standards<br><i>95g/km fleet target enacted</i>",
                 showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor='#2ca02c', ax=-50, ay=-80,
                 xanchor='center', yanchor='bottom', bgcolor='rgba(44,160,44,0.12)', bordercolor='#2ca02c',
                 font=dict(size=11)),
            dict(xref='paper', yref='paper', x=0.92, y=0.00,
                 text="⚠️ 2020: COVID-19 — Temporary slowdown",
                 showarrow=False, bgcolor='rgba(255,255,255,0.95)', bordercolor='#999', borderwidth=1,
                 font=dict(size=11))
        ]

        vrect_title = dict(xref='paper', yref='paper', x=0.92, y=0.97, showarrow=False,
                           text="<b>Global Explosive Growth Era</b>", font=dict(size=14, color='#d62728'))

        fig.add_vrect(x0=2018, x1=2023, fillcolor='rgba(214,39,40,0.12)', line_width=0, layer='below')
        fig.update_layout(annotations=policy_annotations + [vrect_title])

    fig.update_layout(
        title=dict(text='<b>Global EV Stock Growth by Region (2010–2023)</b><br><span style="font-size:12px;color:#666">Policy interventions annotated at key growth inflection points</span>', x=0.5),
        xaxis=dict(title='Year', tickmode='linear', dtick=1, showgrid=True, gridcolor='#E0E0E0'),
        yaxis=dict(title='Total EV Stock (vehicles)', tickformat=',.0f', showgrid=True, gridcolor='#E0E0E0'),
        template='plotly_white', hovermode='x unified', height=650,
        margin=dict(l=80, r=40, t=100, b=80),
        legend=dict(orientation='v', yanchor='top', y=0.99, xanchor='left', x=0.01,
                    bgcolor='rgba(255,255,255,0.9)', bordercolor='#ddd', borderwidth=1),
        paper_bgcolor='#fff', plot_bgcolor='#fafafa'
    )

    return fig


def create_pie_charts(infra_summary: pd.DataFrame, year: int = 2023):
    # Select relevant columns and clean
    charging_latest = infra_summary[['region', 'ev_charging_points']].copy()
    charging_latest = charging_latest.rename(columns={'ev_charging_points': 'total_charging_points'})
    charging_latest = charging_latest.dropna(subset=['total_charging_points'])

    # --- IDENTIFY TOP 5 REGIONS ---
    top5 = charging_latest.nlargest(5, 'total_charging_points')
    top5_regions = top5['region'].tolist()

    # --- AGGREGATE OTHERS INTO "Rest of the world" ---
    charging_latest['region'] = charging_latest['region'].apply(
        lambda r: r if r in top5_regions else 'Rest of the world'
    )

    # Now group again so that all non-top regions merge into one row
    charging_agg = (
        charging_latest.groupby('region', as_index=False)['total_charging_points']
        .sum()
        .sort_values('total_charging_points', ascending=False)
    )

    # ---- USE charging_agg FOR YOUR PIE CHART ----
    # Example (if using matplotlib or plotly):
    # fig = px.pie(charging_agg, names='region', values='total_charging_points', title='EV Charging Points by Region')
    # fig.show()

    return charging_agg

def create_infrastructure_pie_2023(df_sales: pd.DataFrame) -> go.Figure:
    """Create a pie chart of global charging infrastructure distribution for 2023.

    Mirrors notebook logic: filters 'charging points' parameters, aggregates by region,
    keeps top 5 regions and groups the rest into 'Others'. Excludes 'World'.
    """
    df_charging = df_sales[
        (df_sales['parameter'].str.contains('charging points', case=False, na=False)) &
        (df_sales['year'] == 2023)
    ].copy()

    latest_infrastructure_year = 2023

    # Aggregate total charging points by region
    charging_latest = df_charging.groupby('region')['value'].sum().reset_index()
    charging_latest.columns = ['region', 'total_charging_points']

    # Identify top 5 regions
    top5 = charging_latest.nlargest(5, 'total_charging_points')
    top5_names = top5['region'].tolist()

    # Merge all non-top5 regions into "Rest of the world"
    charging_latest['region'] = charging_latest['region'].apply(
        lambda r: r if r in top5_names else 'Rest of the world'
    )

    # Group again because many regions may now be "Rest of the world"
    charging_final = charging_latest.groupby('region')['total_charging_points'].sum().reset_index()

    # Remove "World" if present
    charging_final = charging_final[charging_final['region'] != 'World']

    # Rename "Rest of the world" → "Others"
    charging_final = charging_final.replace({"Rest of the world": "Others"})

    # Create pie chart
    fig = px.pie(
        charging_final,
        values='total_charging_points',
        names='region',
        title=f'Global Charging Infrastructure Distribution ({latest_infrastructure_year})',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        textfont_color='white',
        hovertemplate='<b>%{label}</b><br>Charging Points: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
    )

    return fig

def create_powertrain_sunburst_2023(df_ev_stock: pd.DataFrame) -> go.Figure:
    """Create a sunburst chart of EV stock by Region → Powertrain for 2023.

    Cleaning rules:
    - Filter 2023 only
    - Exclude 'World' and 'EU27'
    - Keep top 4 regions by total EV stock
    - Aggregate all remaining regions into 'Others'
    """

    # --- FILTER TO 2023 & REMOVE WORLD AND EU27 ---
    df_powertrain = df_ev_stock[
        (df_ev_stock['year'] == 2023) &
        (df_ev_stock['region'] != 'World') &
        (df_ev_stock['region'] != 'EU27')
    ].copy()

    # --- IDENTIFY TOP 4 REGIONS ---
    top_regions = (
        df_powertrain.groupby('region')['value']
        .sum()
        .nlargest(3)
        .index
    )

    # --- GROUP EVERYTHING ELSE INTO "Rest of the world" FIRST ---
    df_powertrain["region"] = df_powertrain["region"].apply(
        lambda r: r if r in top_regions else "Rest of the world"
    )

    # --- STANDARDIZE LABEL TO NOTEBOOK CONVENTION ---
    df_powertrain["region"] = df_powertrain["region"].replace(
        {"Rest of the world": "Others"}
    )

    # --- AGGREGATE FINAL DATA FOR SUNBURST ---
    df_sunburst = (
        df_powertrain.groupby(["region", "powertrain"])["value"]
        .sum()
        .reset_index()
    )

    # --- PLOTLY SUNBURST ---
    fig = px.sunburst(
        df_sunburst,
        path=["region", "powertrain"],
        values="value",
        title="EV Stock Hierarchy: Region → Powertrain (2023)"
    )

    fig.update_traces(
        textinfo="label+percent entry",
        texttemplate="%{label}<br>%{percentEntry:.1%}"
    )

    fig.update_layout(
        margin=dict(t=50, l=0, r=0, b=0)
    )

    return fig


def create_powertrain_comparison(df: pd.DataFrame, selected_regions):
    df_powertrain = df[(df['powertrain'].isin(['BEV', 'PHEV'])) & (df['year'] >= 2015) & (df['year'] < 2024)].copy()
    df_yearly_totals = (
        df_powertrain.groupby(['year', 'powertrain'])['ev_stock']
        .sum()
        .reset_index()
        .rename(columns={'ev_stock': 'value'})
    )
    fig = px.bar(
        df_yearly_totals,
        x='year', y='value', color='powertrain', barmode='group',
        title='Yearly Total EV Stock Comparison by Powertrain (2015–2023)',
        labels={'value': 'Total EV Stock (vehicles)', 'year': 'Year', 'powertrain': 'Powertrain Type'},
        color_discrete_map={'BEV': '#E31937', 'PHEV': '#5C5E62'}
    )
    fig.update_layout(height=450, margin=dict(l=60, r=20, t=60, b=50))
    return fig


def create_kpi_card_data(stats: dict):
    return [
        {'title': 'Total Global EV Stock', 'value': f"{stats['total_ev_stock']:,.0f}", 'subtitle': f"Year {stats['year']}"},
        {'title': 'Total Charging Stations', 'value': f"{stats['total_stations']:,.0f}", 'subtitle': 'Globally (2025)'},
        {'title': 'YoY Growth Rate', 'value': f"{stats['yoy_growth_pct']:+.1f}%", 'subtitle': 'Year over Year'}
    ]
