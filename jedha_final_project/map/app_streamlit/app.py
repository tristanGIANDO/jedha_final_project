import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
from folium import DivIcon
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import plotly.express as px
from shapely.geometry import box
# pd.set_option('display.max_rows', None)
from folium.plugins import HeatMap, TimestampedGeoJson
import branca.colormap as cm
import numpy as np


### CONFIG PAGE
st.set_page_config(
    page_title="Get Around Analysis",
    page_icon="🚗",
    layout="wide"
)
st.title('Folium Map in Streamlit')


### INITIALIZE SESSION AND MAP
# Initialize session state for map location and zoom level
if 'map_location' not in st.session_state:
    st.session_state.map_location = [47.98199, 0.1133009]
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 5
# Initialize the Folium map
m = folium.Map(location=st.session_state.map_location, zoom_start=st.session_state.map_zoom)


### DISPLAY ENJEU ZONES
file_path_enjeux_map = "gdf2_BFC.gpkg"

@st.cache_data
def load_data(filepath):
    return gpd.read_file(filepath)

df_enjeux = load_data(file_path_enjeux_map)

# Define the dictionary for enjeux
enjeux_zone_dict = {
    0: {
        'name': 'ZONES REDHIBITOIRES',
        'color': 'white',
        'icon': '🚫'
    },
    1: {
        'name': 'ZONES NON POTENTIELLEMENT FAVORABLES',
        'color': '#FECDFF',
        'icon': '⚠️'
    },
    2: {
        'name': 'ZONES POTENTIELLEMENT FAVORABLES 1',
        'color': '#D086FF',
        'icon': '✅'
    },
    3: {
        'name': 'ZONES POTENTIELLEMENT FAVORABLES 2',
        'color': '#810179',
        'icon': '👍'
    }
}

# Add each enjeu in the map
for enjeu_value in list(enjeux_zone_dict.keys()):
    enjeu = df_enjeux[df_enjeux['enjeu'] == enjeu_value]

    icon_html = f'<span style="font-size: 22px;">{enjeux_zone_dict[enjeu_value]['icon']}</span> {enjeux_zone_dict[enjeu_value]['name']}'
    
    folium.GeoJson(
        enjeu,
        style_function=lambda feature, color=enjeux_zone_dict[enjeu_value]['color']: {
            'fillColor': color,
            'color': 'white',
            'weight': 0,
            'fillOpacity': 0.6
        },
        name=icon_html,
        show=False
    ).add_to(m)


### DISPLAY WIND TURBINES
# Load wind turbine data
@st.cache_data
def load_wind_turbine_data():
    df = pd.read_csv('parcs_eoliens_terrestres.csv')
    return df

wind_turbine_df = load_wind_turbine_data()

wind_turbine_logo_url = "https://www.svgrepo.com/show/530100/wind-energy.svg"


wind_turbine_group = folium.FeatureGroup(name=f'  <img src="{wind_turbine_logo_url}" width="30" height="30" style="vertical-align: middle;"> WIND TURBINES', overlay=True, show=False)


for _, row in wind_turbine_df.iterrows():
    size = 11
    popup_content = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; text-align: center;">
        <img src="{wind_turbine_logo_url}" width="{size}" height="{size}" style="display: block; margin: auto;"/>
        <strong>{row['nom_usuel']}</strong>
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        icon=DivIcon(html=f'<div style="font-size: {size}px;"><img src="{wind_turbine_logo_url}" width="{size}" height="{size}"></div>')
    ).add_to(wind_turbine_group)

wind_turbine_group.add_to(m)



### DISPLAY HEATMAP FOR WIND SPEED
df_wind_speed = pd.read_csv('datameteo_france_1950-2022_clean_02.csv')

# Filter the DataFrame for the specific Year and Month
df_wind_speed_filtered = df_wind_speed[(df_wind_speed['Year'] == 2012) & (df_wind_speed['Month'] == 1)]

# Create a map centered around the mean latitude and longitude of the filtered DataFrame
map_center = [df_wind_speed_filtered['LAT'].mean(), df_wind_speed_filtered['LON'].mean()]
mymap = folium.Map(location=map_center, zoom_start=4)

# Prepare data for the HeatMap (latitude, longitude, and wind speed as intensity)
heat_data = [[row['LAT'], row['LON'], row['vent_speed_inst_moy_mensu']] for index, row in df_wind_speed_filtered.iterrows()]

# Define the colormap
colormap = cm.LinearColormap(colors=['#5F97CF', '#90E1A9', '#F4EB87', '#FFD391', '#D85356'], 
                             vmin=min(df_wind_speed_filtered['vent_speed_inst_moy_mensu']), 
                             vmax=max(df_wind_speed_filtered['vent_speed_inst_moy_mensu']))



wind_speed_logo_url = "https://www.svgrepo.com/show/475599/wind-svg.svg"

heatmap_group = folium.FeatureGroup(name=f'  <img src="{wind_speed_logo_url}" width="30" height="30" style="vertical-align: middle;"> WIND SPEED HEATMAP', overlay=True, show=True)

# Adjust HeatMap parameters
HeatMap(
    heat_data,
    min_opacity=0.01,  # Set lower opacity to reduce intensity
    radius=20,  # Reduce radius to lessen the overlap when zooming out
    blur=10,  # Reduce blur for better definition
).add_to(heatmap_group)

# Add the colormap (color scale) to the map
colormap.caption = 'Wind Speed (m/s)'
colormap.add_to(m)
heatmap_group.add_to(m)



### DISPLAY WIND DIRECTION

wind_direction_group_logo_url = "https://www.svgrepo.com/show/276658/wind-sign-wind.svg"

wind_direction_group = folium.FeatureGroup(name=f'  <img src="{wind_direction_group_logo_url}" width="30" height=" style="vertical-align: middle;"> WIND DIRECTION', overlay=True, show=False)


for idx, row in df_wind_speed_filtered.iterrows():
    wind_direction = row['vent_dir_inst']
    
    # Unique animation name for each arrow
    animation_name = f"moveAndRotate_{idx}"
    
    # Customize these values to adjust animation
    duration = "1s"  # Change to control speed (e.g., "1s", "3s")
    amplitude = 20  # Distance the arrow moves, change as needed
    timing_function = "ease-in-out"  # Options: linear, ease, ease-in, ease-out, ease-in-out

    # Generate unique keyframes animation
    icon_html = f"""
    <div style="
        font-size: 15px;
        color: #183153;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 15px;
        height: 15px;
        animation: {animation_name} {duration} infinite alternate {timing_function};
    ">
        &rarr;
</div>
    <style>
        @keyframes {animation_name} {{
            0% {{ transform: translate(0, 0) rotate({wind_direction}deg); }}
            100% {{ transform: translate({amplitude * np.cos(np.radians(wind_direction))}px, {amplitude * np.sin(np.radians(wind_direction))}px) rotate({wind_direction}deg); }}
        }}
    </style>
    """
    folium.Marker(
        location=[row['LAT'], row['LON']],
        icon=folium.DivIcon(html=icon_html),
        tooltip=f"Wind Speed: {row['vent_speed_inst_moy_mensu']} m/s"
    ).add_to(wind_direction_group)


wind_direction_group.add_to(m)


# # SIDEBAR
# st.sidebar.header("WIND TURBINE ANALYSIS")
# st.sidebar.markdown("""
#     * [1) ](#1-exploratory-data-analysis)
#     * [2) CHECK-IN TYPE AND DELAY ANALYSIS](#2-check-in-type-and-delay-analysis)
#     * [3) IMPACTED RENTALS DUE TO LATE CHECKOUT](#3-impacted-rentals-due-to-late-checkout)
#     * [4) IMPACT OF THRESHOLD](#4-impact-of-threshold)
# """)


# CSS UPDATE OF LAYOUT PANEL
css_file = r"https://j3r3my19.github.io/test/test.css"
css_classes = [
    ('leaflet-control-layers-expanded', css_file),
    ('leaflet-control-layers-expanded-label', css_file)
]
# Append each class to Folium's default CSS
for label, css_file in css_classes:
    folium.folium._default_css.append((label, css_file))


# FINALIZE THE MAP
# Add Layer Control
folium.LayerControl().add_to(m)
map_data = st_folium(m, width="100%", height=650, returned_objects='map')
# Update session state with new map location and zoom level
if map_data:
    st.session_state.map_location = [map_data['center'][0], map_data['center'][1]]
    st.session_state.map_zoom = map_data['zoom']
