"""
Charging stations map component using Folium.
Creates an interactive map with clustered charging station markers.
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl
import os


def create_charging_stations_map(height='600px'):
    """
    Create an interactive Folium map with EV charging stations.
    
    Args:
        height: Height of the map iframe
        
    Returns:
        HTML string containing the Folium map
    """
    try:
        # Load data
        data_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'data', 'processed', 'merged_charging_station', 
            'ev_stations_merged_global.csv'
        )
        
        df = pd.read_csv(data_path)
        df_clean = df.dropna(subset=['lat', 'lon']).copy()
        
        # Calculate map center
        map_center = [df_clean['lat'].median(), df_clean['lon'].median()]
        
        # Create base map
        m = folium.Map(
            location=map_center,
            zoom_start=3,
            tiles='CartoDB positron',  # Clean, light tiles
            prefer_canvas=True,
            max_zoom=18,
            min_zoom=2
        )
        
        # Add dark theme option
        folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)
        
        # Create marker cluster
        marker_cluster = MarkerCluster(
            name='EV Charging Stations',
            overlay=True,
            control=True,
            options={
                'maxClusterRadius': 50,
                'spiderfyOnMaxZoom': True,
                'showCoverageOnHover': False,
                'zoomToBoundsOnClick': True,
                'disableClusteringAtZoom': 15
            }
        ).add_to(m)
        
        # Helper functions
        def get_marker_color(status):
            status_lower = str(status).lower()
            if 'operational' in status_lower and 'not' not in status_lower:
                return 'green'
            elif 'planned' in status_lower:
                return 'blue'
            elif 'temporarily' in status_lower or 'unavailable' in status_lower:
                return 'orange'
            elif 'not operational' in status_lower:
                return 'red'
            return 'gray'
        
        def safe_str(value, default='N/A'):
            if pd.isna(value) or value == '' or value is None:
                return default
            return str(value)
        
        def create_popup_html(row):
            title = safe_str(row.get('title'), 'Unknown Station')
            address = safe_str(row.get('address'))
            town = safe_str(row.get('town'), '')
            state = safe_str(row.get('state'), '')
            country = safe_str(row.get('country'), '')
            operator = safe_str(row.get('operator'), 'Unknown')
            status = safe_str(row.get('status'), 'Unknown')
            connectors = safe_str(row.get('num_connectors'))
            
            location_parts = [p for p in [town, state, country] if p and p != 'N/A' and p != '']
            location = ', '.join(location_parts) if location_parts else 'N/A'
            
            status_color = {
                'Operational': '#28a745',
                'Planned For Future Date': '#007bff',
                'Temporarily Unavailable': '#ffc107',
                'Not Operational': '#dc3545',
                'Unknown': '#6c757d'
            }.get(status, '#6c757d')
            
            return f"""
            <div style="font-family: 'Gotham', Arial, sans-serif; width: 260px;">
                <div style="background: #E31937; color: white; padding: 12px; border-radius: 4px 4px 0 0; margin: -10px -10px 10px -10px;">
                    <h4 style="margin: 0; font-size: 15px; font-weight: 600;">{title}</h4>
                </div>
                <div style="padding: 5px 0;">
                    <p style="margin: 5px 0; font-size: 12px;"><b>Location:</b><br/>{address}<br/>{location}</p>
                    <p style="margin: 5px 0; font-size: 12px;"><b>Operator:</b> {operator}</p>
                    <p style="margin: 5px 0; font-size: 12px;"><b>Connectors:</b> {connectors}</p>
                    <div style="margin-top: 8px;">
                        <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">
                            {status}
                        </span>
                    </div>
                </div>
            </div>
            """
        
        # Add markers (sample for performance if needed)
        sample_size = min(len(df_clean), 5000)  # Limit for performance
        df_sample = df_clean.sample(n=sample_size, random_state=42) if len(df_clean) > sample_size else df_clean
        
        for idx, row in df_sample.iterrows():
            popup_html = create_popup_html(row)
            tooltip_text = f"<b>{row.get('title', 'Unknown')}</b>"
            color = get_marker_color(row.get('status', 'Unknown'))
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=tooltip_text,
                icon=folium.Icon(color=color, icon='plug', prefix='fa')
            ).add_to(marker_cluster)
        
        # Add controls
        folium.LayerControl().add_to(m)
        Fullscreen().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; width: 180px; background-color: white; 
                    border: 1px solid #ddd; border-radius: 4px; z-index: 9999; font-size: 12px; padding: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Gotham', Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0; font-size: 13px; font-weight: 600;">Station Status</h4>
            <p style="margin: 4px 0;"><i class="fa fa-map-marker" style="color: green;"></i> Operational</p>
            <p style="margin: 4px 0;"><i class="fa fa-map-marker" style="color: blue;"></i> Planned</p>
            <p style="margin: 4px 0;"><i class="fa fa-map-marker" style="color: orange;"></i> Temporarily Down</p>
            <p style="margin: 4px 0;"><i class="fa fa-map-marker" style="color: red;"></i> Not Operational</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Return HTML as string
        map_html = m._repr_html_()
        return f'<iframe srcdoc="{map_html}" style="width: 100%; height: {height}; border: none;"></iframe>'
        
    except Exception as e:
        return f'<div style="padding: 20px; color: #E31937;">Error loading map: {str(e)}</div>'


def get_map_html_path():
    """Return path to the saved HTML map file."""
    return os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'output', 
        'ev_stations_global_map.html'
    )
