from flask import Flask, render_template
import pandas as pd
import folium
import numpy as np
from folium import plugins
import branca.colormap as cm

app = Flask(__name__)

@app.route('/')
def index():
    # Load and filter data
    df = pd.read_csv('datameteo_france_1950-2022_clean_02.csv')
    df_filtered = df[(df['Year'] == 2012)]
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
    colormap = cm.LinearColormap(colors=['#5F97CF', '#90E1A9', '#F4EB87', '#FFD391', '#D85356'], 
                                 vmin=min(df_filtered['vent_speed_inst_moy_mensu']), 
                                 vmax=max(df_filtered['vent_speed_inst_moy_mensu']))

    # Create a custom timeline index, labeling forecasted data differently
    timeline_labels = []
    for time_point in time_index:
        if time_point < pd.to_datetime('2012-06-01'):
            timeline_labels.append(time_point.strftime('Historical %Y-%m-%d'))
        else:
            timeline_labels.append(time_point.strftime('Forecast %Y-%m-%d'))

    hm = folium.plugins.HeatMapWithTime(heatmap_data, index=timeline_labels, auto_play=True)
    hm.add_to(mymap)

    # Filter the DataFrame for wind data
    df_filtered_wind = df[(df['Year'] == 2012) & (df['Month'] == 1)]
    wind_direction_group = folium.FeatureGroup(name='Wind Direction', overlay=True, show=False)
    for idx, row in df_filtered_wind.iterrows():
        wind_direction = row['vent_dir_inst']

        # Unique animation name for each arrow
        animation_name = f"moveAndRotate_{idx}"

        # Customize these values to adjust animation
        duration = "1s"
        amplitude = 6
        timing_function = "ease-in-out"

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

    wind_direction_group.add_to(mymap)

    folium.LayerControl().add_to(mymap)

    # Save the map to an HTML file
    map_html = mymap._repr_html_()

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)
