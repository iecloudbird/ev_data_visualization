"""
Chart components for the EV Dashboard.
Contains functions to create all visualizations using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_choropleth_map(df, selected_year):
    """
    Create an interactive choropleth map showing EV stock by country.
    
    Args:
        df: DataFrame with columns: region, year, total_ev_stock, total_stations
        selected_year: Year to display
    
    Returns:
        Plotly figure object
    """
    # ISO country code mapping for choropleth
    region_to_iso = {
        'China': 'CHN', 'USA': 'USA', 'United States': 'USA',
        'Germany': 'DEU', 'France': 'FRA', 'United Kingdom': 'GBR',
        'Japan': 'JPN', 'South Korea': 'KOR', 'Korea': 'KOR',
        'Norway': 'NOR', 'Sweden': 'SWE', 'Netherlands': 'NLD',
        'Italy': 'ITA', 'Spain': 'ESP', 'Belgium': 'BEL',
        'Austria': 'AUT', 'Switzerland': 'CHE', 'Denmark': 'DNK',
        'Canada': 'CAN', 'Australia': 'AUS', 'India': 'IND',
        'Brazil': 'BRA', 'Mexico': 'MEX', 'Thailand': 'THA',
        'Finland': 'FIN', 'Portugal': 'PRT', 'Poland': 'POL',
        'Czechia': 'CZE', 'Greece': 'GRC', 'Turkey': 'TUR',
        'New Zealand': 'NZL', 'Israel': 'ISR', 'South Africa': 'ZAF',
        'Ireland': 'IRL', 'Hungary': 'HUN', 'Romania': 'ROU'
    }
    
    # Filter data for selected year
    df_year = df[df['year'] == selected_year].copy()
    
    # Add ISO codes
    df_year['iso_code'] = df_year['region'].map(region_to_iso)
    
    # Remove unmapped regions (aggregates like "World", "Europe")
    df_mapped = df_year.dropna(subset=['iso_code'])
    
    # Create choropleth with Tesla colors
    fig = px.choropleth(
        df_mapped,
        locations='iso_code',
        color='total_ev_stock',
        hover_name='region',
        hover_data={
            'total_ev_stock': ':,.0f',
            'total_stations': ':,.0f',
            'iso_code': False
        },
        color_continuous_scale=[[0, '#F0F9FF'], [0.2, '#BAE6FD'], [0.5, '#38BDF8'], [0.8, '#0284C7'], [1, '#0C4A6E']],  # Colorblind-safe blue gradient
        title=None,  # Remove title, will be in context description
        labels={'total_ev_stock': 'EV Stock'}
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='#F4F4F4',
            lakecolor='#F4F4F4'
        ),
        height=550,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#FFFFFF',
        font=dict(family='"Gotham", Arial, sans-serif', size=12, color='#171A20'),
        coloraxis_colorbar=dict(
            title=dict(text='EV Stock', font=dict(size=11)),
            thickness=15,
            len=0.7,
            x=1.02
        )
    )
    
    return fig


def create_timeseries_chart(df, selected_regions, metric='total_ev_stock'):
    """
    Create time series line chart showing EV adoption trends.
    
    Args:
        df: DataFrame with region, year, and metric columns
        selected_regions: List of regions to display
        metric: Column name to plot (default: 'total_ev_stock')
    
    Returns:
        Plotly figure object
    """
    # Filter for selected regions
    df_filtered = df[df['region'].isin(selected_regions)].copy()

    df_filtered = df_filtered[df_filtered['region'] != 'EU27']
    
    # Sort for proper line rendering
    df_filtered = df_filtered.sort_values(['region', 'year'])
    
    # Metric labels
    metric_labels = {
        'total_ev_stock': 'Total EV Stock (vehicles)',
        'total_stations': 'Charging Stations',
        'stations_per_ev': 'Stations per EV'
    }
    
    # Tesla color palette for lines
    tesla_colors = ['#E31937', '#171A20', '#5C5E62', '#8C8C8C', '#B8B8B8', 
                    '#CC1A3C', '#2A2D35', '#707277', '#A0A0A0', '#D0D0D0']
    
    fig = px.line(
        df_filtered,
        x='year',
        y=metric,
        color='region',
        title=None,  # Remove title
        labels={
            'year': 'Year',
            metric: metric_labels.get(metric, metric),
            'region': 'Region'
        },
        markers=True,
        color_discrete_sequence=tesla_colors
    )
    
    fig.update_layout(
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E0E0E0',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=60, r=140, t=20, b=50),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#F9F9F9',
        font=dict(family='"Gotham", Arial, sans-serif', size=12, color='#171A20'),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            linecolor='#E0E0E0',
            title_font=dict(size=11, color='#5C5E62')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            linecolor='#E0E0E0',
            title_font=dict(size=11, color='#5C5E62')
        )
    )
    
    # Update line styling
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6)
    )
    
    # Log scale for better visibility if dealing with large ranges
    if metric == 'total_ev_stock':
        fig.update_yaxes(type='log')
    
    return fig


def create_pie_charts(df, selected_year):
    """
    Create two pie charts: infrastructure distribution and adequacy categories.
    
    Args:
        df: DataFrame with infrastructure summary data
        selected_year: Year for analysis
    
    Returns:
        Plotly figure with subplots
    """
    # Get top 10 regions by charging infrastructure
    top_regions = df.nlargest(10, 'ev_charging_points')
    
    # Remove aggregates
    top_regions = top_regions[~top_regions['region'].isin(['World', 'Rest of the world'])]
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{'type':'pie'}]],
        subplot_titles=(
            f'Charging Infrastructure Distribution (Top 10 Regions)',
        )
    )
    
    # Pie 1: Regional distribution
    fig.add_trace(
        go.Pie(
            labels=top_regions['region'],
            values=top_regions['ev_charging_points'],
            name='Infrastructure',
            hovertemplate='<b>%{label}</b><br>Charging Points: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.update_layout(
        height=450,
        showlegend=True,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='#FFFFFF',
        font=dict(family='"Gotham", Arial, sans-serif', size=11, color='#171A20'),
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E0E0E0',
            borderwidth=1
        )
    )
    
    # Update both pies with Tesla styling
    fig.update_traces(
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig


def create_powertrain_comparison(df, selected_regions):
    """
    Create stacked bar chart comparing BEV vs PHEV adoption.
    
    Args:
        df: DataFrame with powertrain data (region, year, powertrain, ev_stock)
        selected_regions: List of regions to display
    
    Returns:
        Plotly figure object
    """
    # Filter for selected regions and exclude very early years
    df_filtered = df[
        (df['region'].isin(selected_regions)) &
        (df['year'] >= 2015) &
        (df['year'] < 2024)
    ].copy()
    
    # Create stacked bar chart with Tesla colors
    fig = px.bar(
        df_filtered,
        x='year',
        y='ev_stock',
        color='powertrain',
        facet_col='region',
        title=None,
        labels={
            'ev_stock': 'EV Stock (vehicles)',
            'year': 'Year',
            'powertrain': 'Powertrain Type'
        },
        color_discrete_map={
            'BEV': '#E31937',  # Tesla Red for BEV
            'PHEV': '#5C5E62',  # Tesla Gray for PHEV
            'FCEV': '#171A20'   # Tesla Black for FCEV
        },
        barmode='stack'
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=60, r=20, t=40, b=50),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#F9F9F9',
        font=dict(family='"Gotham", Arial, sans-serif', size=11, color='#171A20'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E0E0E0',
            borderwidth=1
        ),
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0')
    )
    
    # Update facet styling
    fig.for_each_annotation(lambda a: a.update(
        text=a.text.split("=")[-1],
        font=dict(size=12, color='#171A20', family='"Gotham", Arial, sans-serif')
    ))
    
    # Log scale for better visibility
    fig.update_yaxes(type='log')
    
    return fig

def create_kpi_card_data(stats):
    """
    Format summary statistics for KPI cards.
    
    Args:
        stats: Dictionary with summary statistics
    
    Returns:
        List of dictionaries for KPI cards
    """
    return [
        {
            'title': 'Total Global EV Stock',
            'value': f"{stats['total_ev_stock']:,.0f}",
            'subtitle': f"Year {stats['year']}"
        },
        {
            'title': 'Total Charging Stations',
            'value': f"{stats['total_stations']:,.0f}",
            'subtitle': 'Globally'
        },
        {
            'title': 'Avg Stations per EV',
            'value': f"{stats['avg_stations_per_ev']:.4f}",
            'subtitle': 'Infrastructure Ratio'
        },
        {
            'title': 'YoY Growth Rate',
            'value': f"{stats['yoy_growth_pct']:+.1f}%",
            'subtitle': 'Year over Year'
        }
    ]
