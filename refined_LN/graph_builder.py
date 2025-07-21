from networkx import MultiDiGraph
import json
import networkx as nx
import matplotlib.pyplot as plt

def load_graph_from_json(nodes_path, edges_path):
    with open(nodes_path, 'r') as f:
        nodes_data = json.load(f)["nodes"]
    with open(edges_path, 'r') as f:
        edges_data = json.load(f)["edges"]

    G = MultiDiGraph()
    node_static_info = {}

    for node in nodes_data:
        pub_key = node["pub_key"]
        G.add_node(pub_key)
        node_static_info[pub_key] = {
            "alias": node.get("alias", ""),
            "features": list(node.get("features", {}).values())
        }

    for edge in edges_data:
        G.add_edge(edge["node1_pub"], edge["node2_pub"], **edge)

    return G, node_static_info

def visualize_graph(G, node_static_info, output_path="network_graph.png"):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))

    nx.draw_networkx_nodes(G, pos, node_size=100, node_color="skyblue")

    edge_colors = []
    edge_styles = []
    edges = []

    for u, v, data in G.edges(data=True):
        edges.append((u, v))
        node1_policy = data.get("node1_policy")
        node2_policy = data.get("node2_policy")

        if node1_policy is None and node2_policy is None:
            edge_colors.append("gray")
            edge_styles.append("dashed")
        else:
            edge_colors.append("black")
            edge_styles.append("solid")

    unique_styles = set(edge_styles)
    for style in unique_styles:
        idx = [i for i, s in enumerate(edge_styles) if s == style]
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[edges[i] for i in idx],
            edge_color=[edge_colors[i] for i in idx],
            style=style,
            alpha=0.6
        )

    # ✅ 加上 alias label
    labels = {}
    for node in G.nodes():
        alias = node_static_info.get(node, {}).get("alias", "")
        if alias:
            labels[node] = alias
        else:
            labels[node] = node[:6]  # fallback: 顯示 pubkey 前幾碼

    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.title("Lightning Network Graph Visualization\n(gray dashed = no policy)")
    plt.axis("off")
    plt.savefig(output_path, format="PNG")
    plt.close()


if __name__ == "__main__":
    nodes_path = "nodes_22.json"
    edges_path = "edges_generated.json"

    G, node_static_info = load_graph_from_json(nodes_path, edges_path)
    print(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
    visualize_graph(G, node_static_info)
    print("Graph image saved as 'network_graph.png'")
