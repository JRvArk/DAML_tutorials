import folium
import sqlite3

conn = sqlite3.connect('bridges.sql')
cursor = conn.cursor()

cursor.execute('SELECT latitude, longitude FROM node')
points = cursor.fetchall()

conn.close()

lat = (min([loc[0] for loc in points]) + max([loc[0] for loc in points])) / 2
lon = (min([loc[1] for loc in points]) + max([loc[1] for loc in points])) / 2
m = folium.Map(location=(lat, lon), zoom_start=13)

for lat, lon in points:
    folium.CircleMarker(
        location=(lat, lon),
        size=1,
        fill=True,
        fill_opacity=0.5,
    ).add_to(m)

m.save('bridges_groningen.html')
