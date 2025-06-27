from networkx.readwrite import json_graph
import networkx as nx
import json


# 載入 JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

json_data = load_json('./lnd_test_2.json')

# 建立無向 multigraph
GU = json_graph.node_link_graph(json_data, directed=False, multigraph=True,
                                name='pub_key', source='node1_pub',
                                target='node2_pub', key='channel_id',
                                link='edges')
import matplotlib.pyplot as plt

# 畫圖
plt.figure(figsize=(8, 6))

# 使用 spring layout（有彈性的排版效果）
pos = nx.spring_layout(GU, seed=42)

# 畫節點與邊
nx.draw(GU, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=12, edge_color='gray')

# 可選：在邊上標示 channel_id 或容量
edge_labels = {
    (u, v, k): f"cap:{d['capacity']}" 
    for u, v, k, d in GU.edges(keys=True, data=True)
}
nx.draw_networkx_edge_labels(GU, pos, edge_labels=edge_labels, font_color='red')

# 儲存成 PNG
plt.title("Lightning Network Topology (from lnd_test_1.json)")
plt.tight_layout()
plt.savefig("lightning_topology.png", dpi=300)
plt.show()

# lnd_test_1.json 檔案裡面的東西:
#  "nodes"：節點清單，每個代表一個 Lightning Network 節點（對應一個公鑰）。
#  "edges"：邊的清單，每條邊代表一個開通的 channel（通道），有來源節點、目標節點、通道容量與雙方設定的費用策略。
#  pub_key: 節點的公開金鑰（此處為簡化為 a, b, c…），Lightning Network 中每個節點用公鑰唯一識別。
#  fee_base_msat: 固定手續費(msat為單位)，不論轉多少錢都會收這筆
#  fee_rate_milli_msat: 浮動費率，與金額成比例(ppm（msat/msat）為單位)


# lnd_test_2.json 檔案裡面的東西(老師給的大檔案):
# last_update	    該節點資訊的最後更新時間（UNIX timestamp），用於同步網路資訊時判斷是否需要更新。
# pub_key	        節點的公開金鑰，是辨識該節點的唯一 ID，通常也是通道的對象。
# alias	            節點暱稱，純粹是為了使用者易讀，不具有技術功能。
# addresses	        節點對外的聯網地址（IP 或 Tor）與埠號，是該節點允許被連線的位置，可以支援多個地址。
# color	            節點在圖形化視覺化上的顏色識別碼，與 UI 有關，無實際網路影響。
# features  	    該節點支援的功能旗標（Feature Bits），例如：是否支援多路付款、靜態密鑰、安全關閉等。每個 key 是 feature number，value 描述是否為必要 (is_required)、是否已知 (is_known)。
# custom_records	可擴充的自定義資料欄位，目前為空，供未來擴展用途，例如隱藏型應用等。
#  "last_update":  1748087481,
#             "pub_key":  "0200000000727d3b67513c916f16975e3bf8f3304cf3fcf0ed855e2ae41888f461",
#             "alias":  "lightningspore.com",
#             "addresses":  [
#                 {
#                     "network":  "tcp",
#                     "addr":  "35.84.234.241:9735"
#                 },
#                 {
#                     "network":  "tcp",
#                     "addr":  "[2600:1f14:2069:3900:9716:fea8:2989:800a]:9735"
#                 },
#                 {
#                     "network":  "tcp",
#                     "addr":  "umr3j766h2g67dlythcf4dcs4sjsfvrwybmnmpxobb3xor4l6zkt6uyd.onion:9735"
#                 }
#             ],
#             "color":  "#ff5000",
#             "features":  {
#                 "0":  {
#                     "name":  "data-loss-protect",
#                     "is_required":  true,
#                     "is_known":  true
#                 },