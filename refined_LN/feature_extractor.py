import json
import networkx as nx
from pathlib import Path

# === File paths ===
nodes_path = Path("nodes_22.json")
edges_path = Path("edges_generated.json")
transactions_path = Path("transactions_simulated.json")
dynamic_features_path = Path("node_features.json")
output_path = Path("node_feature_vectors.json")

# === Load JSON data ===
with nodes_path.open() as f:
    raw_nodes = json.load(f)
nodes_data = raw_nodes["nodes"] if isinstance(raw_nodes, dict) and "nodes" in raw_nodes else raw_nodes

with edges_path.open() as f:
    raw_edges = json.load(f)
edges_data = raw_edges["edges"] if isinstance(raw_edges, dict) and "edges" in raw_edges else raw_edges

with transactions_path.open() as f:
    transactions = json.load(f)

with dynamic_features_path.open() as f:
    dynamic_features = json.load(f)

# === Build Graph ===
G = nx.Graph()
for node in nodes_data:
    G.add_node(node["pub_key"], alias=node.get("alias", "unknown"), features=node.get("features", {}))

for edge in edges_data:
    try:
        G.add_edge(edge["node1_pub"], edge["node2_pub"], capacity=int(edge["capacity"]))
    except Exception:
        continue

# === Graph metrics ===
degree_centrality = nx.degree_centrality(G)
clustering = nx.clustering(G)

# === Merge features ===
node_vectors = {}

for node in G.nodes:
    dyn_feat = dynamic_features.get(node, {})
    static_feat = G.nodes[node].get("features", {})
    alias = G.nodes[node].get("alias", "")

    vector = {
        "as_source": dyn_feat.get("as_source", 0),
        "as_target": dyn_feat.get("as_target", 0),
        "as_intermediate": dyn_feat.get("as_intermediate", 0),
        "non_typical_paths": dyn_feat.get("non_typical_paths", 0),
        "success_rate": dyn_feat.get("success_rate", 0.0),
        "degree_centrality": degree_centrality.get(node, 0.0),
        "clustering": clustering.get(node, 0.0),
        "alias": alias
    }

    # 靜態特徵 flags: 支援哪些功能
    for fid, fdata in static_feat.items():
        vector[f"feature_{fid}"] = fdata.get("is_known", False)

    node_vectors[node] = vector

# === Save ===
with output_path.open("w") as f:
    json.dump(node_vectors, f, indent=2)
    print(f"✅ node_feature_vectors.json has been generated.")
