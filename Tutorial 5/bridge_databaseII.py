import osmium
import folium
import sqlite3

# Handler to extract bridge ways and their nodes
class BridgeHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.locations = []

    def node(self, n):
        if 'seamark:type' in n.tags and n.tags['seamark:type'] == 'bridge':
            self.locations.append((n.id, n.lat, n.lon))

    def way(self, w):
        if 'bridge' in w.tags and w.tags['bridge'] == 'yes':
            for node in w.nodes:
                self.locations.append((node.ref, node.lat, node.lon))

        if 'man_made' in w.tags and w.tags['man_made'] == 'bridge':
            for node in w.nodes:
                self.locations.append((node.ref, node.lat, node.lon))


# Initialize the handler and apply it to the PBF file
handler = BridgeHandler()
handler.apply_file('groningen_city.pbf')

# Connect to SQLite database (or create it)
conn = sqlite3.connect('bridgesII.sql')
cursor = conn.cursor()

# Create table for bridge nodes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS node (
        node_id INTEGER PRIMARY KEY,
        latitude REAL,
        longitude REAL
    )
''')

# Insert bridge node data into the database
cursor.executemany(
    'INSERT OR IGNORE INTO node (node_id, latitude, longitude) VALUES (?, ?, ?)',
    handler.locations
)

# Commit and close the database connection
conn.commit()
conn.close()

points = [(loc[1], loc[2]) for loc in handler.locations]

lat = (min([loc[0] for loc in points]) + max([loc[0] for loc in points])) / 2
lon = (min([loc[1] for loc in points]) + max([loc[1] for loc in points])) / 2
m = folium.Map(location=(lat, lon), zoom_start=12)

for lat, lon in points:
    folium.CircleMarker(
        location=(lat, lon),
        radius=4,
        fill=True,
        fill_opacity=0.5,
    ).add_to(m)

m.save('bridges_groningenII.html')

