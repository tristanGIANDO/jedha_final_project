from flask import Flask, render_template
import pandas as pd
import folium
import numpy as np
from folium.plugins import HeatMapWithTime, Fullscreen
import branca.colormap as cm
import os
from folium import DivIcon

app = Flask(__name__)

@app.route('/')
def index():
    df_wind_speed = pd.read_csv('https://jedha-final-project-jrat.s3.amazonaws.com/wind_speed_df.csv')
    df_wind_speed['Date'] = pd.to_datetime(df_wind_speed['Date'])


    mymap = folium.Map(location=[df_wind_speed['LAT'].mean(), df_wind_speed['LON'].mean()], zoom_start=6, min_zoom=6)

    heatmap_data = []
    time_index = df_wind_speed['Date'].sort_values().unique()
    for time_point in time_index:
        data_at_time = df_wind_speed[df_wind_speed['Date'] == time_point]
        heatmap_data.append(data_at_time[['LAT', 'LON', 'wind_speed']].values.tolist())

    timeline_labels = []
    for time_point in time_index:
        if time_point < pd.to_datetime('2023-01-01'):
            timeline_labels.append(time_point.strftime('Historical %Y-%m-%d'))
        else:
            timeline_labels.append(time_point.strftime('Forecast %Y-%m-%d'))

    wind_speed_logo_url = "https://www.svgrepo.com/show/475599/wind-svg.svg"

    HeatMapWithTime(
        name=f'<img src="{wind_speed_logo_url}" width="30" height=" style="vertical-align: middle;"> WIND SPEED',
        data=heatmap_data,
        index=timeline_labels,
        auto_play=False,
        max_opacity=0.4,
        radius=30,
        min_speed=8,
        blur = 0.5,
        use_local_extrema=True,
        gradient={
            0.2: 'rgba(0,0,255,1)',
            0.4: 'green',
            0.6: 'yellow',
            0.8: 'orange',
            1.0: '#FF4D00',    
        },
        position='topleft',
        show=True
    ).add_to(mymap)
    
    custom_css = """
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

    mymap.get_root().html.add_child(folium.Element(custom_css))

    colormap = cm.LinearColormap(colors=['#5F97CF', '#90E1A9', '#F4EB87', '#FFD391', '#D85356'], 
                                    vmin=min(df_wind_speed['wind_speed']), 
                                    vmax=max(df_wind_speed['wind_speed']))

    colormap.caption = 'Wind Speed (Km/h)'
    colormap.add_to(mymap)

    def create_html_table(df_subset):
        table_html = '''
        <div style="max-height: 300px; overflow-y: auto; border:1px solid black; border-collapse:collapse;">
            <table style="width:100%; border:1px solid black; border-collapse:collapse;">
                <thead>
                    <tr style="background-color:#f2f2f2;">
                        <th style="padding:3px; border:1px solid black;">Date</th>
                        <th style="padding:3px; border:1px solid black;">Mean Wind Speed (Km/h)</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for _, row in df_subset.iterrows():
            table_html += f'''
            <tr>
                <td style="padding:3px; border:1px solid black;">{row["Date"].strftime("%Y-%m-%d")}</td>
                <td style="padding:3px; border:1px solid black;">{row["wind_speed"]:.2f}</td>
            </tr>
            '''
        table_html += '''
                </tbody>
            </table>
        </div>
        '''
        return table_html

    for (lat, lon), group in df_wind_speed.groupby(['LAT', 'LON']):
        table_html = create_html_table(group)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=50,
            color='transparent',
            fill=True,
            fill_color='transparent',
            fill_opacity=0,
            popup=folium.Popup(table_html, max_width=300)
        ).add_to(mymap)


    df_wind_dir = pd.read_csv('https://jedha-final-project-jrat.s3.amazonaws.com/wind_dir_df.csv')
    wind_direction_group_logo_url = "https://www.svgrepo.com/show/276658/wind-sign-wind.svg"

    wind_direction_group = folium.FeatureGroup(
        name=f'<img src="{wind_direction_group_logo_url}" width="30" height="30" style="vertical-align: middle;"> WIND DIRECTION <br>(in average for the period 2008-2022)',
        overlay=True,
        show=False
    )
    for idx, row in df_wind_dir.iterrows():
        wind_direction = row['vent_dir_inst'] + 90

        animation_name = f"moveAndRotate_{idx}"
        duration = "1s"
        amplitude = 4
        timing_function = "ease-in-out"

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
            &rarr;
        </div>
        <style>
            @keyframes {animation_name} {{
                0% {{
                    transform: translate(0, 0) rotate({wind_direction}deg);
                    opacity: 1;
                }}
                50% {{
                    transform: translate({amplitude * np.cos(np.radians(wind_direction))}px, {amplitude * np.sin(np.radians(wind_direction))}px) rotate({wind_direction}deg);
                    opacity: 0.8;
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

    allowed_zones_logo_url = "https://www.svgrepo.com/show/311890/check-mark.svg"
    folium.raster_layers.ImageOverlay(
        image="zones_01.png",
        name=f'<img src="{allowed_zones_logo_url}" width="30" height=" style="vertical-align: middle;"> ALLOWED AREAS',
        bounds=[[51.900842276100896, -8.470054815020912], [40.57635104463105, 14.324910985731139]],
        opacity=0.5,
        interactive=False,
        cross_origin=False,
        zindex=1,
        show=False,
        alt="Wikipedia File:Mercator projection SW.jpg",
    ).add_to(mymap)

    wind_turbine_df = pd.read_csv("https://jedha-final-project-jrat.s3.amazonaws.com/parcs_eoliens_terrestres.csv")
    wind_turbine_logo_url = "https://www.svgrepo.com/show/227547/windmill-eolian.svg"
    wind_turbine_group = folium.FeatureGroup(name=f'  <img src="{wind_turbine_logo_url}" width="30" height="30" style="vertical-align: middle;"> WIND TURBINES', overlay=True, show=False)
    for _, row in wind_turbine_df.iterrows():
        size = 20
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

    folium.TileLayer('cartodbpositron', min_zoom=6).add_to(mymap)

    folium.LayerControl().add_to(mymap)
    Fullscreen(position='topright').add_to(mymap)

    map_html = mymap._repr_html_()

    rendered_html = render_template('index.html', map_html=map_html)
    
    # Save the rendered HTML to a file
    with open('final_map.html', 'w') as f:
        f.write(rendered_html)


    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
