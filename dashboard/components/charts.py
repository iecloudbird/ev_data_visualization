# -*- coding: utf-8 -*-
"""
Modernized chart components for the EV Dashboard.
Matches finalized visualizations from ev.ipynb and ev_stations_map.ipynb.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


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


def create_infrastructure_adequacy_scatter(correlation_data: pd.DataFrame) -> go.Figure:
    """Create the infrastructure adequacy scatter used in ev.ipynb section 6.

    X-axis: EV stock 2023 (log), Y-axis: EVs per connector (log).
    Highlights China, USA, Europe and encodes adequacy via color + text box legend.
    """
    # Filter for rows with required fields
    required_cols = ['ev_stock_2023', 'total_connectors_2025', 'evs_per_connector']
    plot_data = correlation_data[correlation_data[required_cols].notna().all(axis=1)].copy()

    if len(plot_data) <= 1:
        # Return an empty-but-valid figure with a helpful title
        fig = go.Figure()
        fig.update_layout(
            title='Infrastructure Adequacy: EV Stock vs EVs per Charging Connector (insufficient data)',
            template='plotly_white'
        )
        return fig

    TARGET_EVS_PER_CHARGER = 30.0

    # Major markets for highlighting
    major_markets = ['China', 'USA', 'Europe']
    plot_data['is_major_market'] = plot_data['region'].isin(major_markets)

    def get_adequacy_color(category: str) -> str:
        color_map = {
            'Adequate': '#4CAF50',      # green
            'Insufficient': '#D32F2F',  # red
            'Well-served': '#2E7D32',   # deep green (legacy)
            'Strained': '#FF9800',      # orange (legacy)
            'Unknown': '#757575',       # gray
        }
        return color_map.get(category, '#757575')

    plot_data['color'] = plot_data['adequacy_category'].apply(get_adequacy_color)

    major_data = plot_data[plot_data['is_major_market']].copy()
    other_data = plot_data[~plot_data['is_major_market']].copy()

    fig = go.Figure()

    # Axis ranges with padding
    x_min = plot_data['ev_stock_2023'].min() * 0.8
    x_max = plot_data['ev_stock_2023'].max() * 2.0
    y_min = plot_data['evs_per_connector'].min() * 0.5
    y_max = plot_data['evs_per_connector'].max() * 1.3

    fig.update_xaxes(
        type="log",
        title_text="<b>EV Stock (2023)</b>",
        title_font=dict(size=14),
        tickfont=dict(size=11),
        gridcolor='lightgray',
        gridwidth=1,
        minor_gridcolor='#f0f0f0',
        showgrid=True,
        range=[np.log10(x_min), np.log10(x_max)],
    )

    fig.update_yaxes(
        type="log",
        title_text="<b>EVs per Charging Connector</b>",
        title_font=dict(size=14),
        tickfont=dict(size=11),
        gridcolor='lightgray',
        gridwidth=1,
        minor_gridcolor='#f0f0f0',
        showgrid=True,
        range=[np.log10(y_min), np.log10(y_max)],
    )

    # Other countries
    if len(other_data) > 0:
        fig.add_trace(
            go.Scatter(
                x=other_data['ev_stock_2023'],
                y=other_data['evs_per_connector'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=other_data['color'],
                    opacity=0.7,
                    line=dict(width=1.5, color='white'),
                    symbol='circle',
                ),
                text=other_data['region'],
                hovertemplate=(
                    '<b>%{text}</b><br>'
                    'EV Stock (2023): %{x:,.0f}<br>'
                    'EVs per Connector: %{y:,.1f}<br>'
                    'Charging Connectors: %{customdata:,.0f}<extra></extra>'
                ),
                customdata=other_data['total_connectors_2025'],
                name='Other Countries',
                showlegend=True,
            )
        )

    # Emphasise major markets with distinct colors
    major_market_colors = {
        'China': '#8E24AA',   # purple
        'USA': '#1976D2',     # blue
        'Europe': '#FF6F00',  # deep orange
    }

    if len(major_data) > 0:
        for _, row in major_data.iterrows():
            marker_size = 12 + max(0, (np.log10(row['ev_stock_2023']) - 4) * 1.2)
            region_name = row['region']
            marker_color = major_market_colors.get(region_name, row['color'])

            fig.add_trace(
                go.Scatter(
                    x=[row['ev_stock_2023']],
                    y=[row['evs_per_connector']],
                    mode='markers',
                    marker=dict(
                        size=marker_size,
                        color=marker_color,
                        opacity=0.9,
                        line=dict(width=2, color='black'),
                        symbol='circle',
                    ),
                    text=[row['region']],
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'EV Stock (2023): %{x:,.0f}<br>'
                        'EVs per Connector: %{y:,.1f}<br>'
                        'Charging Connectors: %{customdata:,.0f}<extra></extra>'
                    ),
                    customdata=[row['total_connectors_2025']],
                    name=row['region'],
                    showlegend=True,
                )
            )

    fig.update_layout(
        height=800,
        width=800,
        title=dict(
            text=(
                '<b>Infrastructure Adequacy: EV Stock vs EVs per Charging Connector</b><br>'
                '<span style="font-size:12px;color:#666">'
                'Comparing 2023 EV stock with 2025 charging connectors'
                '</span>'
            ),
            x=0.5,
            font=dict(size=15),
        ),
        template='plotly_white',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(l=100, r=80, t=120, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
    )

    # Vertical offsets for annotation boxes to avoid overlap
    annotations_y_offset = {
        'China': 0.08,
        'USA': -0.08,
        'Europe': -0.08,
    }

    for _, row in major_data.iterrows():
        region = row['region']
        deficit = row['infrastructure_deficit']
        evs_per_conn = row['evs_per_connector']

        region_annotation_colors = {
            'China': {'bg': 'rgba(142,36,170,0.15)', 'border': '#8E24AA'},
            'USA': {'bg': 'rgba(25,118,210,0.15)', 'border': '#1976D2'},
            'Europe': {'bg': 'rgba(255,111,0,0.15)', 'border': '#FF6F00'},
        }

        if deficit > 100:
            status_text = (
                f"<b>{region}: Severe Reporting Deficit</b><br>"
                f"EVs/Connector: {evs_per_conn:.0f} (Target: {TARGET_EVS_PER_CHARGER:.0f})<br>"
                f"Deficit: +{deficit:.0f} EVs/Charger"
            )
        elif deficit > 0:
            status_text = (
                f"<b>{region}: Infrastructure Deficit</b><br>"
                f"EVs/Connector: {evs_per_conn:.0f} (Target: {TARGET_EVS_PER_CHARGER:.0f})<br>"
                f"Deficit: +{deficit:.0f} EVs/Charger"
            )
        else:
            status_text = (
                f"<b>{region}: Infrastructure Surplus</b><br>"
                f"EVs/Connector: {evs_per_conn:.0f} (Target: {TARGET_EVS_PER_CHARGER:.0f})<br>"
                f"Surplus: {deficit:.0f} EVs/Charger"
            )

        annotation_style = region_annotation_colors.get(
            region,
            {'bg': 'rgba(211,47,47,0.1)', 'border': '#D32F2F'},
        )

        fig.add_annotation(
            x=np.log10(row['ev_stock_2023']),
            y=np.log10(row['evs_per_connector']) + annotations_y_offset.get(region, 0),
            xref='x',
            yref='y',
            text=status_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=annotation_style['border'],
            ax=0,
            ay=-40 if annotations_y_offset.get(region, 0) > 0 else 40,
            bgcolor=annotation_style['bg'],
            bordercolor=annotation_style['border'],
            borderwidth=2,
            borderpad=8,
            font=dict(size=11, color='black'),
            align='left',
        )

    # Adequacy legend textbox
    fig.add_annotation(
        text=(
            '<b>Infrastructure Adequacy Categories:</b><br>'
            '<span style="color:#4CAF50">●</span> Adequate (≤30 EVs/Charger)<br>'
            '<span style="color:#D32F2F">●</span> Insufficient (>30 EVs/Charger)'
        ),
        xref='paper',
        yref='paper',
        x=0.98,
        y=0.98,
        xanchor='right',
        yanchor='top',
        showarrow=False,
        font=dict(size=12, color='#333333', family='Arial, sans-serif'),
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='#666666',
        borderwidth=2,
        borderpad=10,
        align='left',
    )

    return fig
