# detector.py
import json
from collections import defaultdict

NODE_NAME = 4  # 你是 Node B

with open("transaction_logs.json", "r") as f:
    logs = json.load(f)

neighbor_stats = defaultdict(lambda: {'seen': 0, 'failed': 0})

for tx in logs:
    path = tx['path']
    success = tx['success']

    if NODE_NAME in path:
        idx = path.index(NODE_NAME)
        # 觀察 immediate neighbors
        if idx > 0:
            prev_node = path[idx - 1]
            neighbor_stats[prev_node]['seen'] += 1
            if not success:
                neighbor_stats[prev_node]['failed'] += 1
        if idx < len(path) - 1:
            next_node = path[idx + 1]
            neighbor_stats[next_node]['seen'] += 1
            if not success:
                neighbor_stats[next_node]['failed'] += 1

# 判斷「可疑」門檻
print("Immediate neighbors of Node", NODE_NAME)
for neighbor, stats in neighbor_stats.items():
    rate = stats['failed'] / stats['seen'] if stats['seen'] > 0 else 0
    print(f"Neighbor {neighbor}: seen={stats['seen']}  failed={stats['failed']}  fail_rate = {rate * 100:.2f}%")
    if stats['seen'] >= 2 and rate > 0.5:
        print(f"  >> Marked as SUSPICIOUS!")
