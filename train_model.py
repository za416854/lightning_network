import json
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# set up observation model
OBSERVE_NODE = "4"

# load node_features.json and bad_nides data 
with open("node_features.json") as f:
    node_features = json.load(f)
with open("bad_nodes.json") as f:
    bad_nodes = json.load(f)

# ensures observe_node exists
if OBSERVE_NODE not in node_features:
    raise ValueError(f"Node {OBSERVE_NODE} not found in node_features")

# Set neighbors to all other nodes (you can change to neighboring node logic)
neighbors = [nid for nid in node_features if nid != OBSERVE_NODE]
# for nid in node_features:
#     if nid != OBSERVE_NODE:
#         neighbors.append(nid)

X = [] 
y = []
neighbor_ids = []

for nid in neighbors:
    feat = node_features[nid]
    feature_vector = [
        feat.get("as_source", 0),
        feat.get("as_target", 0),
        feat.get("as_intermediate", 0),
        feat.get("non_typical_paths", 0),
        feat.get("success_rate", 0.0),
        feat.get("degree_centrality", 0.0),
        feat.get("clustering", 0.0)
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
    # load true bad nodes data, to set sellar
    with open("bad_nodes.json", "r") as f:
        true_bad_nodes = set(map(int, json.load(f)))
    tp = fp = fn = tn = 0
    # print out predicted result
    for nid, prob in sorted_results:
        label = "❌ Bad" if prob > 0.5 else "✅ Good"
        prefix = "⭐" if int(nid) in true_bad_nodes else ""
        print(f"{prefix} Node {nid}: {label} (Prob = {prob:.2f})")
        
        predicted_bad = prob > 0.5
        actually_bad = int(nid) in true_bad_nodes
        if predicted_bad and actually_bad:
            tp += 1
        elif predicted_bad and not actually_bad:
            fp += 1
        elif not predicted_bad and actually_bad:
            fn += 1
        else:
            tn += 1
            
    print("\n🔎 Bad Node Prediction Accuracy:")
    print(f"⭐ TP (Predicted bad & Actually bad): {tp}")
    print(f"❌ FP (Predicted bad but Actually good): {fp}")
    print(f"🕳️ FN (Missed bad nodes): {fn}")
    print(f"✅ TN (Predicted good & Actually good): {tn}")
    
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    
    print(f"\n🎯 Precision on bad nodes: {precision:.2f}")
    print(f"🔁 Recall on bad nodes: {recall:.2f}")        
        
    with open("local_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("\n✅ Local model saved to local_model.pkl")
