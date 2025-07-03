import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict
import json
from sklearn.feature_extraction import DictVectorizer

# 創建圖形與節點
G = nx.Graph()
nodes = ['A', 'B', 'C', 'D', 'E']
G.add_nodes_from(nodes)
edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('A', 'C'), ('B', 'E')]
G.add_edges_from(edges)

# 選壞節點與產生壞付款
num_bad_nodes = 1
bad_nodes = random.sample(nodes, num_bad_nodes)
num_bad_payments = 10
bad_payments_paths = []

for _ in range(num_bad_payments):
    sender = random.choice(bad_nodes)
    receiver_candidates = [n for n in nodes if n != sender]
    receiver = random.choice(receiver_candidates)
    try:
        path = nx.shortest_path(G, source=sender, target=receiver)
        bad_payments_paths.append(path)
    except nx.NetworkXNoPath:
        continue

# 本地資料表（鄰居對出現次數）
local_data_counts = {node: defaultdict(int) for node in G.nodes()}
for path in bad_payments_paths:
    if len(path) >= 2: # 如果路徑長度大於等於 2（表示路徑中有至少兩個節點，即有實際的付款），才會進行後續處理。
        for i in range(len(path)): # 對每條壞付款路徑中的每個節點進行遍歷(轉發或傳遞壞付款)
            current_node = path[i] # current_node 設為當前遍歷到的節點
            if i > 0 and i < len(path) - 1: # 判斷當前節點是否為中間節點
                prev, nxt = path[i-1], path[i+1]
                local_data_counts[current_node][(prev, nxt)] += 1
            elif i == 0 and len(path) > 1: # 這段代碼處理的是起始節點（路徑的第一個節點），這個節點是壞付款的發送端
                nxt = path[i+1]
                local_data_counts[current_node][('self_source', nxt)] += 1 # self_source: 代表這個節點是壞付款的發送端
            elif i == len(path) - 1 and len(path) > 1: # 這段代碼處理的是結束節點（路徑的最後一個節點）
                prev = path[i-1]
                local_data_counts[current_node][(prev, 'self_sink')] += 1 # self_sink: 代表這個節點是壞付款的接收端


# 使用 DictVectorizer 將本地資料轉換為特徵向量
vectorizer = DictVectorizer(sparse=False)
X = vectorizer.fit_transform(local_data_counts.values())  # 向量化所有節點的資料
feature_names = vectorizer.get_feature_names_out()
print("Feature names (ordered):")
print(feature_names)
# 儲存特徵向量與對應節點
node_features = dict(zip(G.nodes(), X.tolist()))  # 轉換為列表

# 輸出特徵向量到檔案
with open("node_features.json", "w") as f:
    json.dump(node_features, f, indent=2)

# 檢視轉換後的特徵向量
print("Feature vectors for nodes:")
print(node_features)
    
# 繪圖部分
pos = nx.spring_layout(G, seed=42)  # 排版
plt.figure(figsize=(10, 7))

# 畫所有邊
nx.draw_networkx_edges(G, pos, width=1, edge_color='gray')

# 畫節點：壞節點紅色，其餘藍色
nx.draw_networkx_nodes(G, pos, nodelist=G.nodes(), node_color='skyblue', node_size=1200)
nx.draw_networkx_nodes(G, pos, nodelist=bad_nodes, node_color='red', node_size=1200)

# 節點文字
nx.draw_networkx_labels(G, pos, font_color='white', font_weight='bold', font_size=12)

# 畫壞付款路徑（紅色粗線）
for path in bad_payments_paths:
    edges_in_path = list(zip(path[:-1], path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='red', width=3)

# 在每個節點旁邊加上本地觀察表（如 AB:2, C->D:3）
for node, counts in local_data_counts.items():
    info_lines = [f"{a}->{b}:{c}" for (a, b), c in counts.items()]
    info_text = "\n".join(info_lines)
    x, y = pos[node]
    plt.text(x + 0.05, y - 0.05, info_text, fontsize=10, color='black', ha='left', va='top')

plt.title("P2P 壞付款視覺化圖（含節點本地觀察資料）", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
