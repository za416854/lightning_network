import json
import random
import networkx as nx
from datetime import datetime
from collections import defaultdict

# === CONFIGURABLE PARAMETERS ===
NODES_PATH = "nodes_22.json"
EDGES_PATH = "edges_generated.json"
OUTPUT_TRANSACTIONS = "transactions_simulated.json"
OUTPUT_FEATURES = "node_features.json"

NUM_TRANSACTIONS = 1000
BAD_NODES_NUM = 5
MAX_AMOUNT = 1000000

# === Load Graph ===
def load_graph(nodes_path, edges_path):
    with open(nodes_path, "r") as f:
        nodes_data = json.load(f)["nodes"]

    with open(edges_path, "r") as f:
        edges_data = json.load(f)["edges"]

    G = nx.Graph()
    for node in nodes_data:
        G.add_node(node["pub_key"], alias=node.get("alias", ""))

    for edge in edges_data:
        G.add_edge(
            edge["node1_pub"],
            edge["node2_pub"],
            capacity=int(edge["capacity"]),
            node1_policy=edge.get("node1_policy"),
            node2_policy=edge.get("node2_policy")
        )

    return G

# === Select Bad Nodes ===
def select_bad_nodes(G, num_bad):
    return set(random.sample(list(G.nodes), num_bad))

# === Simulate Transactions ===
def simulate_transactions(G, bad_nodes, num_transactions):
    transactions = []
    node_keys = list(G.nodes())

    for _ in range(num_transactions):
        source, target = random.sample(node_keys, 2)
        amount = random.randint(1000, MAX_AMOUNT)
        success = True
        fail_reason = None
        path = []

        try:
            path = nx.shortest_path(G, source=source, target=target)
            total_capacity = 0

            for i in range(len(path) - 1):
                edge = G[path[i]][path[i + 1]]
                cap = edge.get("capacity", 0)
                total_capacity += cap

                policy1 = edge.get("node1_policy")
                policy2 = edge.get("node2_policy")

                if fail_reason is None:
                    if policy1 is None and policy2 is None:
                        success = False
                        fail_reason = "no_policy"
                    elif policy1 and policy1.get("disabled", False):
                        success = False
                        fail_reason = "disabled_channel"
                    elif policy2 and policy2.get("disabled", False):
                        success = False
                        fail_reason = "disabled_channel"

            if fail_reason is None and total_capacity < amount:
                success = False
                fail_reason = "insufficient_capacity"

            if fail_reason is None and (source in bad_nodes or target in bad_nodes):
                success = False
                fail_reason = "bad_node"

        except nx.NetworkXNoPath:
            path = [source, target]
            success = False
            fail_reason = "no_path"

        transactions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "target": target,
            "path": path,
            "success": success,
            "fail_reason": fail_reason,
            "hops": len(path) - 1 if len(path) > 1 else 0,
            "amount": amount
        })

    return transactions

    transactions = []
    node_keys = list(G.nodes())

    for _ in range(num_transactions):
        source, target = random.sample(node_keys, 2)
        amount = random.randint(1000, MAX_AMOUNT)
        success = True
        path = []

        try:
            path = nx.shortest_path(G, source=source, target=target)
            total_capacity = 0

            for i in range(len(path) - 1):
                edge = G[path[i]][path[i + 1]]
                cap = edge.get("capacity", 0)
                total_capacity += cap

                fail_reason = None
                policy1 = edge.get("node1_policy")
                policy2 = edge.get("node2_policy")
                if policy1 is None and policy2 is None:
                    success = False
                    fail_reason = "no_policy"
                elif policy1 and policy1.get("disabled", False):
                    success = False
                    fail_reason = "disabled_channel"
                elif policy2 and policy2.get("disabled", False):
                    success = False
                    fail_reason = "disabled_channel"
                elif total_capacity < amount:
                    success = False
                    fail_reason = "insufficient_capacity"
                elif source in bad_nodes or target in bad_nodes:
                    success = False
                    fail_reason = "bad_node"

            if total_capacity < amount:
                success = False

            if source in bad_nodes or target in bad_nodes:
                success = False

        except nx.NetworkXNoPath:
            path = [source, target]
            success = False

        transactions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "target": target,
            "path": path,
            "success": success,
            "hops": len(path) - 1 if len(path) > 1 else 0,
            "amount": amount
        })

    return transactions

# === Extract Node Features ===
def extract_node_features(G, transactions):
    node_features = defaultdict(lambda: {
        "as_source": 0,
        "as_target": 0,
        "as_intermediate": 0,
        "non_typical_paths": 0,
        "success_rate": 0.0,
        "degree_centrality": 0.0,
        "clustering": 0.0
    })

    success_count = defaultdict(int)
    total_count = defaultdict(int)

    tx_graph = nx.DiGraph()
    for tx in transactions:
        src = tx["source"]
        dst = tx["target"]
        path = tx.get("path", [])
        if len(path) >= 2:
            for i in range(len(path) - 1):
                tx_graph.add_edge(path[i], path[i + 1])
        node_features[src]["as_source"] += 1
        node_features[dst]["as_target"] += 1
        total_count[src] += 1
        if tx["success"]:
            success_count[src] += 1

    for node in tx_graph.nodes():
        node_features[node]["as_intermediate"] = sum(
            1 for nbr in tx_graph.successors(node)
            for nxt in tx_graph.successors(nbr) if nxt != node
        )
        node_features[node]["non_typical_paths"] = node_features[node]["as_intermediate"]

    for node in tx_graph.nodes():
        if total_count[node]:
            node_features[node]["success_rate"] = success_count[node] / total_count[node]

    undirected = tx_graph.to_undirected()
    centrality = nx.degree_centrality(undirected)
    clustering = nx.clustering(undirected)

    for node in tx_graph.nodes():
        node_features[node]["degree_centrality"] = centrality.get(node, 0.0)
        node_features[node]["clustering"] = clustering.get(node, 0.0)

    return node_features

# === MAIN ===
if __name__ == "__main__":
    G = load_graph(NODES_PATH, EDGES_PATH)
    BAD_NODES = select_bad_nodes(G, BAD_NODES_NUM)
    print(f"Selected bad nodes: {BAD_NODES}")

    txs = simulate_transactions(G, BAD_NODES, NUM_TRANSACTIONS)
    node_features = extract_node_features(G, txs)

    with open(OUTPUT_TRANSACTIONS, "w") as f:
        json.dump(txs, f, indent=2)

    with open(OUTPUT_FEATURES, "w") as f:
        json.dump(node_features, f, indent=2)

    print(f"✅ Simulated {NUM_TRANSACTIONS} transactions and extracted features.")
