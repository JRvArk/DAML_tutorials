import osmium
import sqlite3

# Handler to extract bridge ways and their nodes
class BridgeWayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.bridge_nodes = dict()
    def way(self, w):
        if 'bridge' in w.tags and w.tags['bridge'] == 'yes':
            self.bridge_nodes[w.id] = [nd.ref for nd in w.nodes]

# Initialize the handler and apply it to the PBF file
handler = BridgeWayHandler()
handler.apply_file('groningen_city_area.pbf')

bridge_nodes = handler.bridge_nodes

all_node_ids = []
for ids in bridge_nodes.values():
    all_node_ids.extend(ids)

all_node_ids = set(all_node_ids)

class BridgeNode():
    def __init__(self, bridge_id, node_id, lat, lon):
        self.bridge_id = bridge_id
        self.node_id = node_id
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return f"BridgeNode({self.bridge_id, self.node_id, self.lat, self.lon})"

class NodeIDHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.node_locs = dict()
    def node(self, n):
        if n.id in all_node_ids:
            self.node_locs[n.id] = (n.lat, n.lon)

handler = NodeIDHandler()
handler.apply_file('groningen_city_area.pbf')
node_locs = handler.node_locs

nodes = []
for k, v in bridge_nodes.items():
    for nid in v:
        nodes.append(BridgeNode(k, nid, *node_locs[nid]))

# Connect to SQLite database (or create it)
conn = sqlite3.connect('bridges.sql')
cursor = conn.cursor()

# Create table for bridge nodes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS node (
        node_id INTEGER PRIMARY KEY,
        bridge_id INTEGER,
        latitude REAL,
        longitude REAL
    )
''')

# Insert bridge node data into the database
cursor.executemany('INSERT OR IGNORE INTO node (node_id, bridge_id, latitude, longitude) VALUES (?, ?, ?, ?)',
                   [(bn.node_id, bn.bridge_id, bn.lat, bn.lon) for bn in nodes])

# Commit and close the database connection
conn.commit()
conn.close()

print(f"Inserted {len(nodes)} bridge nodes into the database.")
print(f"A total of {len(bridge_nodes)} bridges.")
