import geopandas as gpd
import matplotlib.pyplot as plt
import json
import plotly.express as px
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import folium_static, st_folium
from folium.plugins import HeatMapWithTime
import branca.colormap as cm
import numpy as np

# CONFIG PAGE
st.set_page_config(
    page_title="Wind Speed Forecast",
    page_icon="🌬️",
    layout="wide"
)
st.title('Wind Speed Forecast Map')

# Load and prepare data
df = pd.read_csv('datameteo_france_1950-2022_clean_02.csv')

# Filter the DataFrame for the specific Year
df_filtered = df[df['Year'] == 2012]
df_filtered['Date'] = pd.to_datetime(df_filtered[['Year', 'Month']].assign(DAY=1))

# Group data by time and create a list of heatmap data for each time
heatmap_data = []
time_index = df_filtered['Date'].sort_values().unique()
for time_point in time_index:
    data_at_time = df_filtered[df_filtered['Date'] == time_point]
    heatmap_data.append(data_at_time[['LAT', 'LON', 'vent_speed_inst_moy_mensu']].values.tolist())

# Create the Folium map
mymap = folium.Map(location=[df_filtered['LAT'].mean(), df_filtered['LON'].mean()], zoom_start=6)

# Define the colormap
colormap = cm.LinearColormap(
    colors=['#5F97CF', '#90E1A9', '#F4EB87', '#FFD391', '#D85356'], 
    vmin=df_filtered['vent_speed_inst_moy_mensu'].min(), 
    vmax=df_filtered['vent_speed_inst_moy_mensu'].max()
)

# Create a custom timeline index, labeling forecasted data differently
timeline_labels = []
for time_point in time_index:
    if time_point < pd.to_datetime('2012-06-01'):
        timeline_labels.append(time_point.strftime('Historical %Y-%m-%d'))
    else:
        timeline_labels.append(time_point.strftime('Forecast %Y-%m-%d'))

heatmap_group = folium.FeatureGroup(name='Wind Speed Heatmap', overlay=True, show=True)


# Add the heatmap with time
HeatMapWithTime(
    data=heatmap_data,
    index=timeline_labels,
    auto_play=True,
    max_opacity=0.8,
    radius=10,
    use_local_extrema=True
).add_to(mymap)

# Add the colormap (color scale) to the map
colormap.caption = 'Wind Speed (m/s)'
colormap.add_to(mymap)

# Add Layer Control
folium.LayerControl().add_to(mymap)

# Render the map with folium_static
st_folium(mymap, width=850, height=650)
