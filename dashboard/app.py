"""
Main Dash application for EV Data Visualization Dashboard.
Tesla-inspired modern design with contextual controls.

To run: python -m dashboard.app
Then open http://localhost:8050
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash
from dash import dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
from dashboard.utils.data_loader import EVDataLoader
from dashboard.components.charts import (
    create_choropleth_map,
    create_timeseries_chart,
    create_pie_charts,
    create_powertrain_comparison,
    create_kpi_card_data,
    create_infrastructure_pie_2023,
    create_powertrain_sunburst_2023
)

# Initialize app
app = dash.Dash(
    __name__,
    title='EV Analytics | Tesla Theme',
    update_title='Loading...',
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Gotham:wght@300;400;500;600;700&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)

# Load data
data_loader = EVDataLoader()
print("Loading data...")
ev_data = data_loader.get_ev_stock_by_region_year()
powertrain_data = data_loader.get_powertrain_data()
year_min, year_max = data_loader.get_year_range()
available_regions = data_loader.get_available_regions()
top_regions = data_loader.get_top_regions(n=10, year=year_max)
print(f"✓ Data loaded: {len(ev_data)} records | {year_min}-{year_max}")

# Chart descriptions
CHART_DESCRIPTIONS = {
    'overview_map': {
        'title': 'Global EV Stock Distribution',
        'description': 'Interactive choropleth map showing the distribution of electric vehicles across countries. Enhanced blue gradient highlights regional EV adoption patterns. China, USA, and Europe dominate the global EV market.',
        'controls': ['year-slider']
    },
    'overview_stations': {
        'title': 'EV Charging Infrastructure Network',
        'description': 'Interactive map displaying 12,002 charging stations worldwide with marker clustering. Each station shows operator, location, and status. Zoom in to explore density patterns in specific regions.',
        'controls': []
    },
    'trends_timeseries': {
        'title': 'Global EV Stock Growth by Region (2010–2023)',
        'description': 'Time series with policy annotations showing key drivers: China NEV subsidies (2014, 2018), EU CO₂ standards (2019), and COVID impact (2020). The growth era (2018-2023) is highlighted. Log scale reveals exponential adoption patterns.',
        'controls': ['region-selector']
    },
    'trends_powertrain': {
        'title': 'Yearly Total EV Stock by Powertrain (2015–2023)',
        'description': 'Grouped bar chart comparing BEV (Battery Electric) vs PHEV (Plug-in Hybrid) yearly totals globally. BEV dominance accelerates from 2020 onwards, reflecting market preference for fully electric vehicles.',
        'controls': ['region-selector']
    },
    'breakdown_pie': {
        'title': 'Charging Infrastructure Distribution (2023)',
        'description': 'Top 5 regions by charging points plus "Others". Based on 2023 infrastructure data; controls removed due to non-yearly granularity.',
        'controls': []
    },
    'breakdown_sunburst': {
        'title': 'EV Stock Hierarchy: Region → Powertrain (2023)',
        'description': 'Sunburst showing 2023 EV stock split by top 4 regions and powertrain. Others grouped for readability.',
        'controls': []
    },
}

# Layout
app.layout = html.Div([
    
    # Tesla-style Header
    html.Div([
        html.Div([
            html.Div([
                html.I(className='fas fa-charging-station', style={
                    'fontSize': '28px', 'marginRight': '15px', 'color': '#E31937'
                }),
                html.Span('EV Analytics', style={
                    'fontSize': '24px', 'fontWeight': '600', 'letterSpacing': '0.5px', 'color': '#171A20'
                })
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.P('Global Electric Vehicle Data & Infrastructure Analysis', style={
                'margin': '5px 0 0 43px', 'fontSize': '13px', 'color': '#666', 'fontWeight': '400'
            })
        ], style={'flex': '1'}),
        
        # KPI Cards in Header
        html.Div(id='kpi-cards-header', style={
            'display': 'flex', 'gap': '15px', 'alignItems': 'center'
        })
        
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'padding': '20px 40px',
        'backgroundColor': '#FFFFFF',
        'borderBottom': '1px solid #E0E0E0',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
    }),
    
    # Main Content Area
    html.Div([
        
        # Left Sidebar (Controls)
        html.Div([
            html.Div(id='control-panel-content', children=[
                html.P('Select a visualization to see relevant controls', style={
                    'color': '#999',
                    'fontSize': '13px',
                    'textAlign': 'center',
                    'padding': '20px'
                })
            ])
        ], style={
            'width': '280px',
            'backgroundColor': '#FFFFFF',
            'borderRight': '1px solid #E0E0E0',
            'padding': '30px 20px',
            'overflowY': 'auto',
            'height': 'calc(100vh - 82px)',
            'position': 'sticky',
            'top': '82px'
        }),
        
        # Right Content Area
        html.Div([
            
            # Tab Navigation
            dcc.Tabs(id='main-tabs', value='tab-overview', 
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                
                dcc.Tab(label='Overview', value='tab-overview', 
                       className='custom-tab',
                       selected_className='custom-tab--selected',
                       children=[
                    html.Div([
                        
                        # Chart 1: Choropleth Map
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['overview_map']['title'], 
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['overview_map']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            dcc.Graph(id='choropleth-map', config={'displayModeBar': False})
                        ], className='chart-container'),
                        
                        # Chart 2: Charging Stations Map
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['overview_stations']['title'],
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['overview_stations']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            html.Iframe(
                                id='charging-stations-map',
                                src='/assets/ev_stations_map.html',
                                style={'width': '100%', 'height': '600px', 'border': 'none', 'borderRadius': '4px'}
                            )
                        ], className='chart-container'),
                        
                    ])
                ]),
                
                dcc.Tab(label='Trends', value='tab-trends',
                       className='custom-tab',
                       selected_className='custom-tab--selected',
                       children=[
                    html.Div([
                        
                        # Chart 1: Time Series
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['trends_timeseries']['title'],
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['trends_timeseries']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            dcc.Graph(id='timeseries-chart', config={'displayModeBar': False})
                        ], className='chart-container'),
                        
                        # Chart 2: Powertrain Comparison
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['trends_powertrain']['title'],
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['trends_powertrain']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            dcc.Graph(id='powertrain-comparison', config={'displayModeBar': False})
                        ], className='chart-container'),
                        
                    ])
                ]),
                
                dcc.Tab(label='Breakdown', value='tab-breakdown',
                       className='custom-tab',
                       selected_className='custom-tab--selected',
                       children=[
                    html.Div([
                        
                        # Chart 1: Infrastructure Pie (2023)
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['breakdown_pie']['title'],
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['breakdown_pie']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            dcc.Graph(id='infrastructure-pie', config={'displayModeBar': False})
                        ], className='chart-container'),

                        # Chart 2: Powertrain Sunburst (2023)
                        html.Div([
                            html.Div([
                                html.H3(CHART_DESCRIPTIONS['breakdown_sunburst']['title'],
                                       style={'fontSize': '20px', 'fontWeight': '600', 'margin': '0', 'color': '#FFFFFF'}),
                                html.P(CHART_DESCRIPTIONS['breakdown_sunburst']['description'],
                                      style={'fontSize': '13px', 'color': '#B8B8B8', 'margin': '8px 0 0 0', 'lineHeight': '1.6'})
                            ], style={'marginBottom': '20px'}),
                            dcc.Graph(id='powertrain-sunburst', config={'displayModeBar': False})
                        ], className='chart-container'),
                        
                    ])
                ])
                
            ]),
            
            # Footer
            html.Div([
                html.Div([
                    html.Span('Data Sources: ', style={'color': '#999', 'marginRight': '10px'}),
                    html.A('IEA Global EV Data 2024', href='https://www.kaggle.com/datasets/patricklford/global-ev-sales-2010-2024', target='_blank', style={'color': '#E31937', 'textDecoration': 'none', 'marginRight': '15px'}),
                    html.Span(' | ', style={'color': '#999', 'marginRight': '10px'}),
                    html.A('Global EV Charging Stations (INTL)', href='https://www.kaggle.com/datasets/risheepanchal/global-ev-charging-stations-dataset', target='_blank', style={'color': '#E31937', 'textDecoration': 'none', 'marginRight': '15px'}),
                    html.Span(' | ', style={'color': '#999', 'marginRight': '10px'}),
                    html.A('China EV Charging Stations', href='https://www.cnopendata.com/data/m/poi/POI-cdz.html', target='_blank', style={'color': '#E31937', 'textDecoration': 'none'})
                ], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#999'})
            ], style={'padding': '40px', 'textAlign': 'center', 'borderTop': '1px solid #E0E0E0', 'marginTop': '60px'})
            
        ], style={
            'flex': '1',
            'padding': '30px 40px',
            'backgroundColor': '#F4F4F4',
            'overflowY': 'auto'
        })
        
    ], style={
        'display': 'flex',
        'minHeight': 'calc(100vh - 82px)'
    }),
    
    # Hidden divs for state management
    html.Div(id='current-tab', style={'display': 'none'}),
    dcc.Store(id='year-store', data=year_max),  # Store for year value
    dcc.Store(id='region-store', data=top_regions[:5]),  # Store for regions
    dcc.Store(id='metric-store', data='total_ev_stock'),  # Store for metric
    
], style={
    'fontFamily': '"Gotham", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
    'margin': '0',
    'padding': '0',
    'backgroundColor': '#F4F4F4'
})


# Callbacks

@app.callback(
    Output('kpi-cards-header', 'children'),
    [Input('year-slider-overview', 'value')]
)
def update_kpi_cards(year_overview):
    """Update KPI cards in header based on year slider value."""
    # Use overview slider value
    year = year_overview if year_overview else year_max
    
    stats = data_loader.calculate_summary_stats(year=year)
    kpi_data = create_kpi_card_data(stats)
    
    cards = []
    icons = ['fa-car-side', 'fa-charging-station', 'fa-chart-line']
    
    for i, kpi in enumerate(kpi_data[:3]):  # Show top 3 KPIs
        card = html.Div([
            html.Div([
                html.I(className=f'fas {icons[i]}', style={'fontSize': '16px', 'color': '#E31937'}),
            ], style={'marginBottom': '8px'}),
            html.Div(kpi['value'], style={
                'fontSize': '20px',
                'fontWeight': '600',
                'color': '#171A20',
                'marginBottom': '4px'
            }),
            html.Div(kpi['title'], style={
                'fontSize': '11px',
                'color': '#5C5E62',
                'fontWeight': '500',
                'textTransform': 'uppercase',
                'letterSpacing': '0.5px'
            })
        ], style={
            'padding': '15px 20px',
            'backgroundColor': '#F9F9F9',
            'borderRadius': '4px',
            'minWidth': '140px',
            'textAlign': 'center',
            'border': '1px solid #E0E0E0'
        })
        cards.append(card)
    
    return cards


@app.callback(
    [Output('control-panel-content', 'children'),
     Output('current-tab', 'children')],
    [Input('main-tabs', 'value'),
     Input('choropleth-map', 'hoverData'),
    Input('timeseries-chart', 'hoverData'),
    Input('infrastructure-pie', 'hoverData'),
    Input('powertrain-sunburst', 'hoverData')]
)
def update_sidebar_controls(active_tab, *args):
    """Update sidebar with contextual controls based on active tab."""
    
    controls = []
    
    # Title
    controls.append(html.H3('Controls', style={
        'fontSize': '16px',
        'fontWeight': '600',
        'color': '#171A20',
        'marginBottom': '25px',
        'textTransform': 'uppercase',
        'letterSpacing': '1px'
    }))
    
    if active_tab == 'tab-overview':
        # Year slider for overview
        controls.extend([
            html.Label('Year', style={'fontSize': '12px', 'fontWeight': '600', 'color': '#171A20', 'marginBottom': '10px', 'display': 'block', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
            dcc.Slider(
                id='year-slider-overview',
                min=year_min,
                max=year_max,
                value=year_max,
                marks={year: {'label': str(year), 'style': {'fontSize': '10px', 'color': '#5C5E62'}} for year in range(year_min, year_max + 1, 3)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": True},
                className='tesla-slider'
            ),
            html.Div(style={'height': '30px'})
        ])
        
    elif active_tab == 'tab-trends':
        # Region selector for trends (no metric selector - finalized chart shows EV stock with policy annotations)
        controls.extend([
            html.Label('Regions', style={'fontSize': '12px', 'fontWeight': '600', 'color': '#171A20', 'marginBottom': '10px', 'display': 'block', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
            dcc.Dropdown(
                id='region-selector',
                options=[{'label': region, 'value': region} for region in available_regions],
                value=top_regions[:8],
                multi=True,
                placeholder='Select regions...',
                className='tesla-dropdown',
                style={'marginBottom': '25px'}
            ),
            html.P('💡 Chart displays EV stock trends with key policy annotations (China NEV subsidies, EU CO₂ standards, COVID impact)', 
                   style={'fontSize': '11px', 'color': '#666', 'fontStyle': 'italic', 'marginTop': '10px'})
        ])
        
    elif active_tab == 'tab-breakdown':
        controls.extend([
            html.P('No controls for breakdown charts (2023 data only).',
                   style={'fontSize': '12px', 'color': '#666'})
        ])
    
    return controls, active_tab


@app.callback(
    Output('choropleth-map', 'figure'),
    Input('year-slider-overview', 'value')
)
def update_choropleth(year):
    """Update choropleth map."""
    year = year if year else year_max
    return create_choropleth_map(ev_data, year)


@app.callback(
    Output('timeseries-chart', 'figure'),
    Input('region-selector', 'value')
)
def update_timeseries(selected_regions):
    """Update time series chart with policy annotations."""
    if not selected_regions:
        selected_regions = top_regions[:8]
    return create_timeseries_chart(ev_data, selected_regions, show_annotations=True)


@app.callback(
    Output('infrastructure-pie', 'figure'),
    Input('current-tab', 'children')
)
def update_infrastructure_pie(_active_tab):
    """Render 2023 infrastructure pie chart using notebook-style aggregation."""
    # Use notebook-matching data prep from IEA sales dataset
    charging_final = data_loader.get_charging_points_distribution_2023()
    fig = px.pie(
        charging_final,
        values='total_charging_points',
        names='region',
        title='Global Charging Infrastructure Distribution (2023)',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12,
        textfont_color='white',
        hovertemplate='<b>%{label}</b><br>Charging Points: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
    )
    return fig


@app.callback(
    Output('powertrain-sunburst', 'figure'),
    Input('current-tab', 'children')
)
def update_powertrain_sunburst(_active_tab):
    """Render 2023 powertrain sunburst without controls."""
    df_ev_stock = powertrain_data[['region', 'year', 'powertrain', 'ev_stock']].copy()
    df_ev_stock = df_ev_stock.rename(columns={'ev_stock': 'value'})
    return create_powertrain_sunburst_2023(df_ev_stock)


@app.callback(
    Output('powertrain-comparison', 'figure'),
    Input('region-selector', 'value')
)
def update_powertrain_comparison(selected_regions):
    """Update powertrain comparison chart."""
    if not selected_regions:
        selected_regions = top_regions[:5]
    return create_powertrain_comparison(powertrain_data, selected_regions)


# Run server
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 EV Analytics Dashboard - Tesla Theme")
    print("="*60)
    print(f"📊 {len(ev_data)} records loaded ({year_min}-{year_max})")
    print(f"🌍 {len(available_regions)} regions available")
    print(f"🔗 http://localhost:8050")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
