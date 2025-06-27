import json
import networkx as nx
import matplotlib.pyplot as plt

# 讀取 JSON 檔案
with open('lnd_test_2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 建立有向圖
G = nx.DiGraph()

# 加入節點
for node in data["nodes"]:
    pub_key = node["pub_key"]
    alias = node.get("alias", "")
    color = node.get("color", "#000000")
    
    G.add_node(pub_key, alias=alias, color=color)

# 加入通道（邊）
if "edges" in data:
    for edge in data["edges"]:
        node1 = edge["node1_pub"]
        node2 = edge["node2_pub"]
        capacity = int(edge.get("capacity", 0))
        
        # 加入 node1 → node2 的費用資訊
        policy1 = edge.get("node1_policy") or {}
        base_fee_1 = int(policy1.get("fee_base_msat", 0))
        rate_fee_1 = int(policy1.get("fee_rate_milli_msat", 0))
        
        policy2 = edge.get("node2_policy") or {}
        base_fee_2 = int(policy2.get("fee_base_msat", 0))
        rate_fee_2 = int(policy2.get("fee_rate_milli_msat", 0))

        
        # 雙向邊（LN 中每個方向都可能有不同費率）
        G.add_edge(node1, node2, capacity=capacity, base_fee=base_fee_1, rate_fee=rate_fee_1)
        G.add_edge(node2, node1, capacity=capacity, base_fee=base_fee_2, rate_fee=rate_fee_2)

# 只標記少數節點（例如度數前幾名）
high_degree_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:50]
subG = G.subgraph([n for n, _ in high_degree_nodes])
subG = subG.copy()
subG.remove_nodes_from(list(nx.isolates(subG)))  # 移除沒有邊的節點

pos = nx.spring_layout(subG, seed=42)
# 顯示 alias（若沒有 alias，就顯示前 6 碼 pub_key）
labels = {
    n: G.nodes[n].get("alias") or n[:6]
    for n in subG.nodes
}

plt.figure(figsize=(20, 16))  # 更大畫布
nx.draw(subG, pos, with_labels=False, node_size=300, node_color='orange', edge_color='gray')
nx.draw_networkx_labels(subG, pos, labels=labels, font_size=10)
plt.title("Top 50 High-Degree Nodes", fontsize=14)
plt.show()
