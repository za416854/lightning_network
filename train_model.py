import json
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
# set up observation model
# OBSERVE_NODE = "4"

# False True
feature_flags = {
    "as_source": True,
    "as_target": True,
    "as_intermediate": True,
    "non_typical_paths": True,
    "success_rate": True,
    "degree_centrality": True,
    "clustering": True,
    "parallel_channel_count": True
}


# load node_features.json and bad_nodes data 
with open("node_features.json") as f:
    node_features = json.load(f)
with open("bad_nodes.json") as f:
    bad_nodes = json.load(f)

# Choose OBSERVE_NODE randomly from non-bad nodes
all_node_ids = list(node_features.keys())
clean_node_ids = [nid for nid in all_node_ids if int(nid) not in bad_nodes]
OBSERVE_NODE = random.choice(clean_node_ids)

print(f"👁️ Randomly selected observer node: {OBSERVE_NODE}")

# ensures observe_node exists
if OBSERVE_NODE not in node_features:
    raise ValueError(f"Node {OBSERVE_NODE} not found in node_features")

# Set neighbors to all other nodes (you can change to neighboring node logic)
neighbors = [nid for nid in node_features if nid != OBSERVE_NODE]

# dynamically get feature names (excluding the observed node)
# sample_features = node_features[next(iter(node_features))]
# feature_keys = list(sample_features.keys())

X = [] 
y = []
neighbor_ids = []

for nid in neighbors:
    feat = node_features[nid]
    # feature_vector = [
    #     feat.get("as_source", 0),
    #     feat.get("as_target", 0),
    #     feat.get("as_intermediate", 0),
    #     feat.get("non_typical_paths", 0),
    #     feat.get("success_rate", 0.0),
    #     feat.get("degree_centrality", 0.0),
    #     feat.get("clustering", 0.0),
    #     feat.get("parallel_channel_count", 0)
    # ]

    feature_vector = [feat.get(k, 0.0) for k, use in feature_flags.items() if use]

    
    label = 1 if int(nid) in bad_nodes else 0
    X.append(feature_vector)
    y.append(label)
    neighbor_ids.append(nid)
    
selected_features = [k for k, use in feature_flags.items() if use]
# print(f"🧬 Using features: {selected_features}")
    
X = np.array(X)
y = np.array(y)

print(f"📦 Original data size: {len(X)}")
X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, neighbor_ids, test_size=0.2, random_state=42, stratify=y
)
print(f"📦 Training set size: {len(X_train)} ({len(X_train)/len(X):.0%})")
print(f"🧪 Test set size: {len(X_test)} ({len(X_test)/len(X):.0%})")


# print(f"\n👁️ Observer Node: {OBSERVE_NODE}")

# Choose which ML model to use: "logistic", "random_forest", "svm", "xgboost"
MODEL_TYPE = "svm"

if len(set(y)) < 2:
    print("⚠️ Not enough class diversity to train (only one class present).\n")
else:
    if MODEL_TYPE == "logistic":
        clf = LogisticRegression()
    elif MODEL_TYPE == "random_forest":
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
    elif MODEL_TYPE == "svm":
        clf = SVC(probability=True, kernel="rbf")
    elif MODEL_TYPE == "xgboost":
        clf = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {MODEL_TYPE}")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred))

    print("\n🧮 Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\n🔍 Suspicious Neighbors (sorted by bad prob):")
    sorted_results = sorted(zip(id_test, y_prob), key=lambda x: -x[1])
    true_bad_nodes = set(map(int, bad_nodes))
    
    tp = fp = fn = tn = 0
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
    
    print(f"\n🔎 Observing {len(X)} neighbors with {len(selected_features)} features: {selected_features}")
    print(f"\n🎯 Precision on bad nodes: {precision:.2f}")
    print(f"🔁 Recall on bad nodes: {recall:.2f}")        
        
    with open("local_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("\n✅ Local model saved to local_model.pkl")
