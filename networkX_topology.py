import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict
import json
from sklearn.feature_extraction import DictVectorizer

# ---------- 🔧 User adjustable parameters----------
NUM_NODES = 10
NUM_BAD_NODES = 1
NUM_BAD_PAYMENTS = 50

INCLUDE_GOOD_PAYMENTS = True
NUM_GOOD_PAYMENTS = 20

# ---------- Generate Node ----------
nodes = [chr(ord('A') + i) if i < 26 else f"N{i}" for i in range(NUM_NODES)]

# ---------- Create a graph ----------
G = nx.Graph()
G.add_nodes_from(nodes)

# ---------- Randomly generate connections (at least 2 per node)----------
edges = set()
for node in nodes:
    others = list(set(nodes) - {node})
    neighbors = random.sample(others, min(2, len(others)))
    for neighbor in neighbors:
        edge = tuple(sorted([node, neighbor]))
        edges.add(edge)
G.add_edges_from(edges)
# think about algo to sim source, destinatiom and paths 0707
# ---------- Selecting bad nodes and generating bad payments ----------
bad_nodes = random.sample(nodes, min(NUM_BAD_NODES, len(nodes)))
bad_payments_paths = []
for _ in range(NUM_BAD_PAYMENTS):
    sender = random.choice(bad_nodes)
    receiver_candidates = [n for n in nodes if n != sender]
    receiver = random.choice(receiver_candidates)
    try:
        path = nx.shortest_path(G, source=sender, target=receiver)
        bad_payments_paths.append(path)
    except nx.NetworkXNoPath:
        continue

# ---------- Generate good people payment ----------
good_payments_paths = []
if INCLUDE_GOOD_PAYMENTS:
    good_nodes = list(set(nodes) - set(bad_nodes))
    for _ in range(NUM_GOOD_PAYMENTS):
        sender = random.choice(good_nodes)
        receiver_candidates = [n for n in good_nodes if n != sender]
        if not receiver_candidates:
            continue
        receiver = random.choice(receiver_candidates)
        try:
            path = nx.shortest_path(G, source=sender, target=receiver)
            good_payments_paths.append(path)
        except nx.NetworkXNoPath:
            continue

# ---------- Building local observation data ----------
local_data_counts = {node: defaultdict(int) for node in G.nodes()}
all_paths = bad_payments_paths + good_payments_paths
for path in all_paths:
    if len(path) >= 2:
        for i in range(len(path)):
            current_node = path[i]
            if i > 0 and i < len(path) - 1:
                prev, nxt = path[i-1], path[i+1]
                local_data_counts[current_node][(prev, nxt)] += 1
            elif i == 0 and len(path) > 1:
                nxt = path[i+1]
                local_data_counts[current_node][('self_source', nxt)] += 1
            elif i == len(path) - 1 and len(path) > 1:
                prev = path[i-1]
                local_data_counts[current_node][(prev, 'self_sink')] += 1

# ---------- Feature Vectorization ----------
vectorizer = DictVectorizer(sparse=False)
X = vectorizer.fit_transform(local_data_counts.values())
feature_names = vectorizer.get_feature_names_out()
print("🔍 Feature name:")
print(feature_names)

# save grath to JSON file 0707 
# networkX to save to files 0707
# ---------- Storing feature vectors and labels ----------
node_features = dict(zip(G.nodes(), X.tolist()))
with open("node_features.json", "w") as f:
    json.dump(node_features, f, indent=2)

with open("bad_nodes.json", "w") as f:
    json.dump(bad_nodes, f)

print("✅ Feature vector output completed, total", len(node_features), "pen")

# ---------- Drawing ----------
pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(12, 9))
nx.draw_networkx_edges(G, pos, width=1, edge_color='gray')
nx.draw_networkx_nodes(G, pos, nodelist=G.nodes(), node_color='skyblue', node_size=1000)
nx.draw_networkx_nodes(G, pos, nodelist=bad_nodes, node_color='red', node_size=1000)
nx.draw_networkx_labels(G, pos, font_color='white', font_weight='bold', font_size=10)

# Indicates the bad payment path (red) and the good payment path (green)
for path in bad_payments_paths:
    edges_in_path = list(zip(path[:-1], path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='red', width=3)

if INCLUDE_GOOD_PAYMENTS:
    for path in good_payments_paths:
        edges_in_path = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='green', width=2)

# Plot statistics for each node
for node, counts in local_data_counts.items():
    info_lines = [f"{a}->{b}:{c}" for (a, b), c in counts.items()]
    info_text = "\n".join(info_lines)
    x, y = pos[node]
    plt.text(x + 0.05, y - 0.05, info_text, fontsize=8, color='black', ha='left', va='top')

plt.title(f"P2P Payment Visualization: {NUM_NODES} nodes, {NUM_BAD_NODES} bad nodes", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
