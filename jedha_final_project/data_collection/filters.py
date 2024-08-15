import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
import random
from collections import defaultdict


def is_in_zone(coords: tuple[float, float],
               zone: list[tuple[float, float]]) -> bool:
    """Verify if a place is in a zone

    Args:
        coords (tuple[float, float]): position station meteo ou parc eolien
        zone (list[tuple[float, float]]): zone d'autorisation

    Returns:
        bool

    Example:
        coords = (43.02, 1.05)
        zone = [(50.1, -3), (48.3, 5), (32.5, -1), (25.2, 3), (40.0, 2.5)]
        result = is_in_zone(coords, zone)
        print(result)
    """
    x, y = coords
    n = len(zone)
    inside = False

    p1x, p1y = zone[0]
    for i in range(n + 1):
        p2x, p2y = zone[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


# df = pd.read_csv("s3://jedha-final-project-jrat/zones.csv")

# print(df.head())

# global_zone = df[["Latitude", "Longitude"]]
# global_zone = list(global_zone.itertuples(index=False, name=None))

# coordinates = [
#     (random.uniform(45, 50),
#      random.uniform(0, 7)) for _ in range(200)
# ]

# km = KMeans(n_clusters=100, random_state=0, init="k-means++")
# km.fit(global_zone)

# df["cluster"] = km.labels_

# # fig = px.scatter_mapbox(df,
# #                         lat="Latitude",
# #                         lon="Longitude",
# #                         color="cluster",
# #                         mapbox_style="carto-positron")
# # fig.show()

# clusters = defaultdict(list)

# for _, entry in df.iterrows():
#     lat_lon_tuple = (entry["Latitude"], entry["Longitude"])
#     clusters[entry["cluster"]].append(lat_lon_tuple)

# zones = list(clusters.values())


# green_points = []

# for zone in zones:
#     for place in coordinates:
#         if place in green_points:
#             continue
#         if is_in_zone(place, zone):
#             green_points.append(place)

# red_points = list(set(coordinates) - set(green_points))

# fig = px.scatter_mapbox(df,
#                         lat="Latitude",
#                         lon="Longitude")
#                         # color="cluster")  # mapbox_style="carto-positron")

# fig.add_scattermapbox(lat=[point[0] for point in green_points],
#                       lon=[point[1] for point in green_points],
#                       mode="markers",
#                       marker=dict(size=10, color="green"),
#                       name="In Zone")

# fig.add_scattermapbox(lat=[point[0] for point in red_points],
#                       lon=[point[1] for point in red_points],
#                       mode="markers",
#                       marker=dict(size=10, color="red"),
#                       name="Out of Zone")

# fig.update_layout(mapbox_style="open-street-map")
# fig.show()


import numpy as np

df = pd.read_csv("s3://jedha-final-project-jrat/zones.csv")

global_zone = df[["Latitude", "Longitude"]]
global_zone = list(global_zone.itertuples(index=False, name=None))

coordinates = [(random.uniform(42, 50.5), random.uniform(0, 7)) for _ in range(1000)]

km = KMeans(n_clusters=30, random_state=1, init="k-means++")
km.fit(global_zone)
df["cluster"] = km.labels_

fig = px.scatter_mapbox(df,
                        lat="Latitude",
                        lon="Longitude",
                        color="cluster",
                        mapbox_style="carto-positron")
fig.show()


clusters = defaultdict(list)
for _, entry in df.iterrows():
    lat_lon_tuple = (entry["Latitude"], entry["Longitude"])
    clusters[entry["cluster"]].append(lat_lon_tuple)

zones = list(clusters.values())


points = []
for coord in coordinates:
    point_color = 'red'
    for zone in zones:
        if is_in_zone(coord, zone):
            point_color = 'green'
            break
    points.append((*coord, point_color))


zone_points = [(row["Latitude"], row["Longitude"], 'blue') for _, row in df.iterrows()]
all_points = zone_points + points

plot_df = pd.DataFrame(all_points, columns=["Latitude", "Longitude", "Color"])

fig = px.scatter_mapbox(plot_df,
                        lat="Latitude",
                        lon="Longitude",
                        color="Color",
                        mapbox_style="carto-positron",
                        zoom=5)
fig.update_layout(mapbox={'center': {'lat': 50.1, 'lon': 3.4}})
fig.show()
