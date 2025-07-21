# pip install scikit-learn matplotlib

import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression

# ========= 1. Loading data =========
with open("node_features.json", "r") as f:
    node_features = json.load(f)

# ========= 2. Prepare X (features) and y (labels) =========
# 假設 "A" 是壞節點（label=1），其他是好節點（label=0）
X = [] # 每個節點的 input 向量(特徵資料)（像身高、連線數、交易數等）
y = [] # 告訴模型：這個節點是好人還是壞人（0 或 1）(答案標籤)
node_names = [] # 節點名稱清單

# Read the bad node list from networkX_topology.py output
with open("bad_nodes.json", "r") as f:
    bad_nodes = json.load(f)

for node, features in node_features.items():
    X.append(features)
    y.append(1 if node in bad_nodes else 0)
    node_names.append(node)

X = np.array(X)
y = np.array(y)

# ========= 3. Split training/testing data =========
X_train, X_test, y_train, y_test, name_train, name_test = train_test_split(
    X, y, node_names, test_size=0.4, random_state=42
)
# X_train: 機器看到這些特徵來「學習」
# X_test: 機器沒看過，用來考它的表現
# y_test： 測試資料的「真實答案」 → ground truth
# test_size: 測試資料佔比 40%，如果你有 100 筆資料，那就是 60 筆訓練 / 40 筆測試
# random_state: 固定亂數種子，每次切的結果都一樣（可重現）

# ========= 4. Building and training models =========
# random_state=42 的意思是「鎖定隨機數生成的起點，讓所有依賴隨機性的操作（如資料切分）在每次執行時都產生相同的、可預測的結果」。# Logistic Regression

# clf = LogisticRegression(class_weight='balanced')

# random forest 
# clf = RandomForestClassifier(n_estimators=100, random_state=42)

# SVC model （Support Vector Classifier）
clf = SVC(kernel='rbf', probability=True)
clf = SVC(kernel='rbf', probability=True, class_weight='balanced', random_state=42)

# XGBoost 
# clf = XGBClassifier(
#     n_estimators=100,
#     max_depth=3,
#     learning_rate=0.1,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     scale_pos_weight=len(y_train[y_train==0])/len(y_train[y_train==1]),  # 處理不平衡
#     random_state=42
# )

# Try model stacking
estimators = [
    ('svc', SVC(kernel='rbf', probability=True, class_weight='balanced', random_state=42)),
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
]

clf = StackingClassifier(
    estimators=estimators,
    final_estimator=LogisticRegression(),
    cv=5
)

clf.fit(X_train, y_train) # 「訓練速度」測量的就是這一行的執行時間！

# ========= 5. 模型預測與評估 =========
y_pred = clf.predict(X_test) # 執行預測
y_prob = clf.predict_proba(X_test)[:, 1]  #  計算機率

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred)) #計算評估指標

print("📘 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ========= 6. Display the prediction results for each node =========
print("\n🔍 Node prediction probability:")
threshold = 0.3
for name, prob in zip(name_test, y_prob):
    label = 1 if prob >= threshold else 0
    print(f"Node {name}: predicted as {'bad' if label == 1 else 'good'} (probability = {prob:.2f})")
# ========= 7. Optional: Visualize the predicted probabilities =========
plt.figure(figsize=(8, 4))
plt.bar(name_test, y_prob, color=['red' if p >= threshold else 'blue' for p in y_prob])
plt.axhline(threshold, color='gray', linestyle='--')
plt.title("The probability of each node being predicted to be a bad node")
plt.ylabel("probability")
plt.show()
