# pip install scikit-learn matplotlib

import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

# ========= 1. 載入資料 =========
with open("node_features.json", "r") as f:
    node_features = json.load(f)

# ========= 2. 準備 X（特徵）與 y（標籤） =========
# 假設 "A" 是壞節點（label=1），其他是好節點（label=0）
X = []
y = []
node_names = []

for node, features in node_features.items():
    X.append(features)
    y.append(1 if node == "A" else 0)  # 自訂壞節點標籤規則
    node_names.append(node)

X = np.array(X)
y = np.array(y)

# ========= 3. 拆分訓練/測試資料 =========
X_train, X_test, y_train, y_test, name_train, name_test = train_test_split(
    X, y, node_names, test_size=0.4, random_state=42
)

# ========= 4. 建立與訓練模型 =========
clf = LogisticRegression()
clf.fit(X_train, y_train)

# ========= 5. 模型預測與評估 =========
y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]  # 機率值

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

print("📘 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ========= 6. 顯示每個節點預測結果 =========
print("\n🔍 節點預測機率：")
for name, prob, label in zip(name_test, y_prob, y_pred):
    print(f"節點 {name}: 預測為 {'壞' if label == 1 else '好'} (機率 = {prob:.2f})")

# ========= 7. 可選：視覺化預測機率 =========
plt.figure(figsize=(8, 4))
plt.bar(name_test, y_prob, color=['red' if p >= 0.5 else 'blue' for p in y_prob])
plt.axhline(0.5, color='gray', linestyle='--')
plt.title("The probability of each node being predicted to be a bad node")
plt.ylabel("probability")
plt.show()
