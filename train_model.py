# train_local_model.py
import json
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# 設定觀察節點
OBSERVE_NODE = "4"

# 載入資料
with open("node_features.json") as f:
    node_features = json.load(f)
with open("bad_nodes.json") as f:
    bad_nodes = json.load(f)

# 確認 observe_node 存在
if OBSERVE_NODE not in node_features:
    raise ValueError(f"Node {OBSERVE_NODE} not found in node_features")

# 取得 neighbors（這邊假設 features 裡有記錄 neighbor 資訊，或你要自己另外載入圖結構）
# 簡單假設 neighbors 為所有其他節點（你可替換為真的 neighbors 資訊）
neighbors = [nid for nid in node_features if nid != OBSERVE_NODE]

X, y, neighbor_ids = [], [], []
for nid in neighbors:
    feat = node_features[nid]
    feature_vector = [
        feat.get("as_source", 0),
        feat.get("as_target", 0),
        feat.get("as_intermediate", 0),
        feat.get("non_typical_paths", 0)
    ]
    label = 1 if int(nid) in bad_nodes else 0

    X.append(feature_vector)
    y.append(label)
    neighbor_ids.append(nid)

X = np.array(X)
y = np.array(y)

print(f"\n👁️ Observer Node: {OBSERVE_NODE}")
print(f"🔎 Observing {len(X)} neighbors\n")

if len(set(y)) < 2:
    print("⚠️ Not enough class diversity to train (only one class present).\n")
else:
    # 模型訓練
    clf = LogisticRegression()
    clf.fit(X, y)

    y_pred = clf.predict(X)
    y_prob = clf.predict_proba(X)[:, 1]

    print("📊 Classification Report:")
    print(classification_report(y, y_pred))

    print("\n🧮 Confusion Matrix:")
    print(confusion_matrix(y, y_pred))

    print("\n🔍 Suspicious Neighbors (sorted by bad prob):")
    sorted_results = sorted(zip(neighbor_ids, y_prob), key=lambda x: -x[1])
    for nid, prob in sorted_results:
        label = "❌ Bad" if prob > 0.5 else "✅ Good"
        print(f"Node {nid}: {label} (Prob = {prob:.2f})")

    # 模型儲存
    with open("local_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("\n✅ Local model saved to local_model.pkl")
