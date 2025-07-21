import json
import networkx as nx
import random
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

NUM_NODES = 1000
NUM_TRANSACTIONS = 3000
BAD_NODES_NUM = 200

# Define bad nodes randomly
BAD_NODES = random.sample(range(NUM_NODES), BAD_NODES_NUM)

# Generate transactions
transactions = []
for _ in range(NUM_TRANSACTIONS):
    src = random.randint(0, NUM_NODES - 1)
    dst = random.randint(0, NUM_NODES - 1)
    while dst == src:
        dst = random.randint(0, NUM_NODES - 1)
    success = not (src in BAD_NODES or dst in BAD_NODES)
    transactions.append({"source": src, "target": dst, "success": success})

# Parallel channel feature: how many parallel edges this node is involved in
parallel_channel_count = defaultdict(int)
edge_counter = defaultdict(int)

for tx in transactions:
    key = (tx["source"], tx["target"])
    edge_counter[key] += 1

for (src, dst), count in edge_counter.items():
    if count > 1:  # Only count if it's a true parallel connection
        parallel_channel_count[src] += 1
        parallel_channel_count[dst] += 1

with open("transaction_logs.json", "w") as f:
    json.dump(transactions, f, indent=2)
with open("bad_nodes.json", "w") as f:
    json.dump(BAD_NODES, f)

# Create directed graph from transactions
G = nx.DiGraph()
for tx in transactions:
    G.add_edge(tx["source"], tx["target"])

# Initialize node features
node_features = defaultdict(lambda: {
    "as_source": 0,
    "as_target": 0,
    "as_intermediate": 0,
    "non_typical_paths": 0,
    "success_rate": 0.0,
    "degree_centrality": 0.0,
    "clustering": 0.0
})

# Count sources and targets
for tx in transactions:
    src = tx["source"]
    dst = tx["target"]
    node_features[str(src)]["as_source"] += 1
    node_features[str(dst)]["as_target"] += 1

# Count intermediate appearances and non-typical paths
for node in G.nodes:
    node_str = str(node)
    node_features[node_str]["parallel_channel_count"] = parallel_channel_count.get(node, 0)
    for nbr in G.successors(node):
        for nxt in G.successors(nbr):
            if nxt != node:
                node_features[str(node)]["as_intermediate"] += 1
    node_features[str(node)]["non_typical_paths"] = sum(
        1 for nbr in G.successors(node)
        for nxt in G.successors(nbr) if nxt != node
    )

# Success rate per node as source
success_count = defaultdict(int)
total_count = defaultdict(int)
for tx in transactions:
    src = tx["source"]
    total_count[src] += 1
    if tx["success"]:
        success_count[src] += 1

for node in G.nodes:
    node_str = str(node)
    if total_count[node]:
        node_features[node_str]["success_rate"] = success_count[node] / total_count[node]
    else:
        node_features[node_str]["success_rate"] = 0.0

# Centrality and clustering
undirected_G = G.to_undirected()
centrality = nx.degree_centrality(undirected_G)
clustering = nx.clustering(undirected_G)

for node in G.nodes:
    node_str = str(node)
    node_features[node_str]["degree_centrality"] = centrality.get(node, 0.0)
    node_features[node_str]["clustering"] = clustering.get(node, 0.0)

# Save node features
with open("node_features.json", "w") as f:
    json.dump(node_features, f, indent=2)

# Draw graph
# 📍 Network Drawing
pos = nx.spring_layout(G, seed=42)

# Edge of picture (light gray background)
nx.draw_networkx_edges(G, pos, alpha=0.3)

# Draw nodes: bad nodes are red, normal nodes are blue
node_colors = ['red' if node in BAD_NODES else 'lightblue' for node in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=8)

# Highlight all failed transaction paths (red)
for tx in transactions:
    if not tx.get("success"):
        path = tx.get("path", [tx["source"], tx["target"]])  # fallback for old tx format
        edge_list = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color='red', width=1.5, alpha=0.7)

plt.title("Transaction Graph with Bad Nodes Highlighted")
plt.axis('off')
plt.tight_layout()
plt.savefig("graph_output.jpg")
plt.close()


print("✅ Transaction graph + features saved.")
