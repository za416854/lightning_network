import json
import pickle
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

# ==== Load features & labels ====
with open("node_feature_vectors.json") as f:
    node_features = json.load(f)

with open("bad_nodes.json") as f:
    bad_nodes = set(json.load(f))

test_size = 0.2

# ==== Feature selection flags ====
feature_flags = {
    "as_source": True,
    "as_target": True,
    "as_intermediate": True,
    "non_typical_paths": True,
    "success_rate": True,
    "degree_centrality": True,
    "clustering": True,
}

# ==== Build X, y ====
X = []
y = []
node_ids = []

for node_id, features in node_features.items():
    vec = [features.get(k, 0) for k, v in feature_flags.items() if v]
    X.append(vec)
    y.append(1 if node_id in bad_nodes else 0)
    node_ids.append(node_id)

X = np.array(X)
y = np.array(y)

print(f"📦 Total nodes: {len(X)}")

# ==== Ensure at least one bad node in test ====
bad_indices = [i for i, nid in enumerate(node_ids) if nid in bad_nodes]
good_indices = [i for i, nid in enumerate(node_ids) if nid not in bad_nodes]

# 固定挑出一個壞節點放入 test
test_bad_index = random.choice(bad_indices)
remaining_indices = list(set(range(len(X))) - {test_bad_index})
random.shuffle(remaining_indices)

test_size_count = int(len(X) * test_size) - 1
test_indices = [test_bad_index] + remaining_indices[:test_size_count]
train_indices = list(set(range(len(X))) - set(test_indices))

X_train = X[train_indices]
y_train = y[train_indices]
id_train = [node_ids[i] for i in train_indices]

X_test = X[test_indices]
y_test = y[test_indices]
id_test = [node_ids[i] for i in test_indices]

print(f"🧪 Training size: {len(X_train)} | Testing size: {len(X_test)}")

# ==== Show bad nodes in training and test ====
# print("\n🔑 Bad nodes in training:")
# print([nid[:6] for nid in id_train if nid in bad_nodes])

print("🔑 Bad nodes in test:")
print([nid[:6] for nid in id_test if nid in bad_nodes])

# ==== Select Model ====
MODEL_TYPE = "random_forest"  # Options: logistic, random_forest, svm, xgboost

if MODEL_TYPE == "logistic":
    clf = LogisticRegression()
elif MODEL_TYPE == "random_forest":
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
elif MODEL_TYPE == "svm":
    clf = SVC(probability=True, kernel="rbf")
elif MODEL_TYPE == "xgboost":
    clf = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
else:
    raise ValueError("Unsupported MODEL_TYPE")


# ==== Train Model ====
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]


# ==== Show feature coefficients if logistic ====
if MODEL_TYPE == "logistic":
    feature_names = [k for k, v in feature_flags.items() if v]
    print("\n🔍 Dynamic feature Coefficients:")
    for name, coef in zip(feature_names, clf.coef_[0]):
        direction = '+' if coef > 0 else '-'
        print(f"{name:25}: {direction}{abs(coef):.4f}")
        
# ==== Report ====
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

print("🧮 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ==== Sort by suspicious level ====
print("\n🔍 Suspicious Nodes (by probability):")
sorted_nodes = sorted(zip(id_test, y_prob), key=lambda x: -x[1])

# 取前 N 個為預測的壞節點
num_actual_bad = len([nid for nid in id_test if nid in bad_nodes])
predicted_bad_nodes = {nid for nid, _ in sorted_nodes[:num_actual_bad]}

tp = fp = fn = tn = 0
for nid, prob in sorted_nodes:
    is_bad = nid in bad_nodes
    predicted = nid in predicted_bad_nodes
    label = "❌ Bad" if predicted else "✅ Good"
    prefix = "⭐" if is_bad else ""
    print(f"{prefix} Node {nid[:6]}...: {label} (Prob = {prob:.2f})")

    if predicted and is_bad:
        tp += 1
    elif predicted and not is_bad:
        fp += 1
    elif not predicted and is_bad:
        fn += 1
    else:
        tn += 1

# ==== Metrics ====
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0

print(f"\n🎯 Precision: {precision:.2f}")
print(f"🔁 Recall: {recall:.2f}")


# ==== Save model ====
with open("trained_model.pkl", "wb") as f:
    pickle.dump(clf, f)
print("✅ Model saved to trained_model.pkl")
