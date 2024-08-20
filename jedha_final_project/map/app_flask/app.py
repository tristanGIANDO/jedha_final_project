from flask import Flask, render_template
import pandas as pd
import folium
import numpy as np
from folium import plugins
from folium.plugins import HeatMap, TimestampedGeoJson, HeatMapWithTime
import branca.colormap as cm
import os
import geopandas as gpd
from folium import DivIcon


# CONFIG FLASK
app = Flask(__name__)

@app.route('/')
def index():
    # Load and filter data
    df = pd.read_csv('datameteo_france_1950-2022_clean_02.csv')
    df_filtered = df[(df['Year'] == 2012)]
    df_filtered['Date'] = pd.to_datetime(df_filtered[['Year', 'Month']].assign(DAY=1))

    # Create the Folium map
    mymap = folium.Map(location=[df_filtered['LAT'].mean(), df_filtered['LON'].mean()], zoom_start=6)


    # HEATMAP
    # Group data by time and create a list of heatmap data for each time
    heatmap_data = []
    time_index = df_filtered['Date'].sort_values().unique()
    for time_point in time_index:
        data_at_time = df_filtered[df_filtered['Date'] == time_point]
        heatmap_data.append(data_at_time[['LAT', 'LON', 'vent_speed_inst_moy_mensu']].values.tolist())

    # Create a custom timeline index, labeling forecasted data differently
    timeline_labels = []
    for time_point in time_index:
        if time_point < pd.to_datetime('2012-06-01'):
            timeline_labels.append(time_point.strftime('Historical %Y-%m-%d'))
        else:
            timeline_labels.append(time_point.strftime('Forecast %Y-%m-%d'))
            
    wind_speed_logo_url = "https://www.svgrepo.com/show/475599/wind-svg.svg"

    # Add the heatmap with time
    HeatMapWithTime(
        name=f'<img src="{wind_speed_logo_url}" width="30" height=" style="vertical-align: middle;"> WIND SPEED',  # Naming the layer
        index=timeline_labels,  # Use the custom timeline labels
        data=heatmap_data,
        auto_play=False,
        max_opacity=0.2,
        radius=30,
        use_local_extrema=True,
        position='topleft'  # Change the position of the timeline
    ).add_to(mymap)

    # Inject custom CSS to adjust timeline size
    map_script_timeline_control = """
    <style>
    .leaflet-bar-timecontrol { /* Adjust the timeline control size */
        top: 10px;     /* Adjust top position */
        left: auto;    /* Adjust left position */
    }
    /* Change the background color of the control layer */
    .leaflet-control-layers-expanded {
        background-color: #c5d9e3; /* Change this to your desired color */
    }

    /* Change the text color of the control layer */
    .leaflet-control-layers-expanded {
        color: #0f0f0f; /* Change this to your desired color */
    }
    </style>
    """
    mymap.get_root().html.add_child(folium.Element(map_script_timeline_control))

    # JavaScript to reposition the timeline control before the zoom control
    # Move the zoom and layer controls to the top right
    map_script_zoom_layer_control = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        // Find the zoom control and layer control elements
        var zoomControl = document.querySelector("div.leaflet-control-zoom");
        var layersControl = document.querySelector("div.leaflet-control-layers");
        
        if (zoomControl) {
            // Move the zoom control
            zoomControl.style.position = 'absolute';
            zoomControl.style.top = '60px';
            zoomControl.style.right = 'auto';
            zoomControl.style.left = 'auto';
        }

        if (layersControl) {
            // Move the layer control
            layersControl.style.position = 'absolute';
            layersControl.style.top = '60px';  // Adjust this value based on zoom control height
            layersControl.style.right = '20px';
            layersControl.style.left = 'auto';
        }
    });
    </script>
    """

    # Add the JavaScript to the map
    mymap.get_root().html.add_child(folium.Element(map_script_zoom_layer_control))



        # Define the colormap
    colormap = cm.LinearColormap(colors=['#5F97CF', '#90E1A9', '#F4EB87', '#FFD391', '#D85356'], 
                                 vmin=min(df_filtered['vent_speed_inst_moy_mensu']), 
                                 vmax=max(df_filtered['vent_speed_inst_moy_mensu']))
    
    # Add the colormap (color scale) to the map
    colormap.caption = 'Wind Speed (m/s)'
    colormap.add_to(mymap)


    def create_html_table(df_subset):
        # Define the table style with padding for cells
        table_html = '''
        <table style="width:100%; border:1px solid black; border-collapse:collapse;">
            <tr style="background-color:#f2f2f2;">
                <th style="padding:3px; border:1px solid black;">Date</th>
                <th style="padding:3px; border:1px solid black;">Wind Speed (m/s)</th>
            </tr>
        '''
        # Add rows with padding
        for _, row in df_subset.iterrows():
            table_html += f'''
            <tr>
                <td style="padding:3px; border:1px solid black;">{row["Date"].strftime("%Y-%m-%d")}</td>
                <td style="padding:3px; border:1px solid black;">{row["vent_speed_inst_moy_mensu"]:.2f}</td>
            </tr>
            '''
        table_html += '</table>'
        return table_html
    
    # Add popups with tables
    for (lat, lon), group in df_filtered.groupby(['LAT', 'LON']):
        table_html = create_html_table(group)
        
        # Create a large clickable area using CircleMarker
        folium.CircleMarker(
            location=[lat, lon],
            radius=20,  # Adjust the radius as needed
            color='transparent',  # Make it invisible
            fill=True,
            fill_color='transparent',
            fill_opacity=0,
            popup=folium.Popup(table_html, max_width=300)
        ).add_to(mymap)



    # WIND DIRECTION
    # Filter the DataFrame for wind data
    df_filtered_wind = df[(df['Year'] == 2012) & (df['Month'] == 1)]

    wind_direction_group_logo_url = "https://www.svgrepo.com/show/276658/wind-sign-wind.svg"


    wind_direction_group = folium.FeatureGroup(name=f'<img src="{wind_direction_group_logo_url}" width="30" height=" style="vertical-align: middle;"> WIND DIRECTION', overlay=True, show=False)

    for idx, row in df_filtered_wind.iterrows():
        wind_direction = row['vent_dir_inst']

        # Unique animation name for each arrow
        animation_name = f"moveAndRotate_{idx}"

        # Customize these values to adjust animation
        duration = "1s"
        amplitude = 7
        timing_function = "ease-in-out"

        # Generate unique keyframes animation with fade
        icon_html = f"""
        <div style="
            font-size: 20px;
            color: #5573C3;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: {animation_name} {duration} infinite alternate {timing_function};
        ">
            &rArr;
        </div>
        <style>
            @keyframes {animation_name} {{
                0% {{
                    transform: translate(0, 0) rotate({wind_direction}deg);
                    opacity: 1;
                }}
                50% {{
                    transform: translate({amplitude * np.cos(np.radians(wind_direction))}px, {amplitude * np.sin(np.radians(wind_direction))}px) rotate({wind_direction}deg);
                    opacity: 0.6;
                }}
                100% {{
                    transform: translate(0, 0) rotate({wind_direction}deg);
                    opacity: 1;
                }}
            }}
        </style>
        """
        folium.Marker(
                location=[row['LAT'], row['LON']],
                icon=folium.DivIcon(html=icon_html)
            ).add_to(wind_direction_group)

    wind_direction_group.add_to(mymap)


    # ENJEUX ZONE
    allowed_zones_logo_url = "https://www.svgrepo.com/show/311890/check-mark.svg"
    df_allowed_zones = pd.read_csv("https://jedha-final-project-jrat.s3.amazonaws.com/zones_03.csv")
    heatmap_data_allowed_zones = df_allowed_zones[['LAT', 'LON']].values.tolist()
    HeatMap(
        name=f'<img src="{allowed_zones_logo_url}" width="30" height=" style="vertical-align: middle;"> ZONES POTENTIELLEMENT FAVORABLES',  # Naming the layer
        data=heatmap_data_allowed_zones,
        radius=5,           # Adjust the radius of each point
        blur=8,             # Adjust the blur of the points
        min_opacity=0.3,
        gradient={0: 'rgba(163,84,141,0)', 1: 'rgba(163,84,141,1)'},  # Custom color gradient,
        show = False
    ).add_to(mymap)

    # WIND TURBINES LOCATION
    wind_turbine_df = pd.read_csv('parcs_eoliens_terrestres.csv')
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
    wind_turbine_group.add_to(mymap)


    folium.LayerControl().add_to(mymap)


    # Save the map to an HTML file
    map_html = mymap._repr_html_()

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

