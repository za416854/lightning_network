import networkx as nx
import matplotlib.pyplot as plt
import random

# 創建一個簡單的圖形
G = nx.Graph()
nodes = ['A', 'B', 'C', 'D', 'E'] # 5個節點
G.add_nodes_from(nodes)

# 添加邊
edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('A', 'C'), ('B', 'E')]
G.add_edges_from(edges)

print("圖形節點:", G.nodes())
print("圖形邊緣:", G.edges())

# 隨機選擇壞節點
num_bad_nodes = 1 # 可以根據需要調整
bad_nodes = random.sample(list(G.nodes()), num_bad_nodes)
print("壞節點:", bad_nodes)
# 模擬壞付款
num_bad_payments = 10 # 模擬的壞付款數量
bad_payments_paths = []

for _ in range(num_bad_payments):
    sender = random.choice(bad_nodes) # 壞付款從壞節點發起

    # 隨機選擇接收節點，確保不與發送節點相同
    possible_receivers = [node for node in G.nodes() if node != sender]
    if not possible_receivers:
        continue # 如果沒有其他節點可以接收，則跳過

    receiver = random.choice(possible_receivers)

    try:
        # 計算最短路徑 (假設所有邊權重為1，即最短路徑就是邊數最少)
        path = nx.shortest_path(G, source=sender, target=receiver)
        bad_payments_paths.append(path)
    except nx.NetworkXNoPath:
        print(f"從 {sender} 到 {receiver} 沒有路徑。")
        continue

print("\n模擬的壞付款路徑:")
for path in bad_payments_paths:
    print(path)
    
# ---- 繪圖 ----
# 建立節點位置（自動排版）
pos = nx.spring_layout(G, seed=42)

# 先畫全部的邊與節點
nx.draw_networkx_edges(G, pos, width=1, edge_color='gray')
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800)

# 突顯壞節點
nx.draw_networkx_nodes(G, pos, nodelist=bad_nodes, node_color='red', node_size=800)

# 畫節點標籤
nx.draw_networkx_labels(G, pos, font_color='white', font_weight='bold')

# 顯示每條壞付款的路徑（用紅線畫出）
for path in bad_payments_paths:
    edge_list = list(zip(path[:-1], path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edge_list, width=3, edge_color='red')

plt.title("P2P Network diagram (bad nodes and bad payment paths)")
plt.axis('off')
plt.show()