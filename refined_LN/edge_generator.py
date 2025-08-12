import json
import random
import uuid
import time

# None
allow_null_prob = 0
def generate_channel_policies(allow_null_prob=allow_null_prob):
    if random.random() < allow_null_prob:
        return None, None  # both sides null to simulate unsynced or inactive channel
    return generate_policy(), generate_policy()

def generate_policy(allow_null=True):
    # if allow_null and random.random() < 0.1:
    #     return None  # 10% chance to simulate missing policy
    
    return {
        "time_lock_delta": random.choice([18, 40, 80, 144]),
        "min_htlc": str(random.choice([1000, 5000, 10000])),
        "fee_base_msat": str(random.choice([0, 1000, 2000, 3000])),
        "fee_rate_milli_msat": str(random.choice([1, 10, 20, 50, 100])),
        "disabled": random.choice([False] * 10 + [True] * 0),  # disabled is rare
        "max_htlc_msat": str(random.randint(10000000, 1980000000)),
        "last_update": int(time.time()),
        "custom_records": {},
        "inbound_fee_base_msat": random.choice([0, 1000]),
        "inbound_fee_rate_milli_msat": random.choice([0, 1, 5, 10])
    }


import hashlib
from itertools import combinations
from typing import List

def load_nodes(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [node['pub_key'] for node in data['nodes'] if 'pub_key' in node]

def generate_channel_id_and_point(index: int) -> (str, str):
    base = f"channel_{index}_{uuid.uuid4()}"
    channel_id = int(hashlib.sha256(base.encode()).hexdigest(), 16) % (1 << 64)
    chan_point_txid = hashlib.sha256((base + "_tx").encode()).hexdigest()
    chan_point_index = random.randint(0, 1)
    return str(channel_id), f"{chan_point_txid}:{chan_point_index}"
# 從所有可能的節點對中，最多選出你要的通道數量，但不要超過可用的總數。
def generate_edges(pub_keys: List[str], num_edges: int, allow_parallel: bool = False) -> List[dict]:
    channels = []
    pair_set = set()

    all_possible_pairs = list(combinations(pub_keys, 2)) # 給你一個清單，它會幫你列出「不重複的所有可能兩兩組合（或多個）」。["A", "B", "C"] => [('A', 'B'), ('A', 'C'), ('B', 'C')]
    if not allow_parallel:
        random.shuffle(all_possible_pairs)
        selected_pairs = all_possible_pairs[:min(num_edges, len(all_possible_pairs))] # 你說你要 num_edges 條通道，但我最多只能給你現有的 len(all_possible_pairs) 條！」，這樣可以避免你說要 100 條通道，但節點只有 5 個，根本湊不出那麼多。
    else:
        selected_pairs = [tuple(random.sample(pub_keys, 2)) for _ in range(num_edges)]

    for i, pair in enumerate(selected_pairs):
        node1, node2 = pair
        channel_id, chan_point = generate_channel_id_and_point(i)
        capacity = str(random.randint(10000, 1000000))
        node1_policy, node2_policy = generate_channel_policies()
        channels.append({
            "channel_id": channel_id,
            "chan_point": chan_point,
            "last_update": 0,
            "node1_pub": node1,
            "node2_pub": node2,
            "capacity": capacity,
            "node1_policy": node1_policy,
            "node2_policy": node2_policy,
            "custom_records": {}
        })

    return channels


def save_edges(edges: List[dict], output_path: str):
    with open(output_path, 'w') as f:
        json.dump({"edges": edges}, f, indent=4)

if __name__ == "__main__":
    node_file_path = "nodes_200.json"  # your input node file
    output_file_path = "edges_generated.json"
    NUM_EDGES = 500  # adjustable
    ALLOW_PARALLEL_CHANNELS = False  # toggle this for parallel channel behavior

    pub_keys = load_nodes(node_file_path)
    print(f" nodes number from {node_file_path}: {len(pub_keys)}")
    # print(f"節點公鑰: {pub_keys}")
    edges = generate_edges(pub_keys, NUM_EDGES, allow_parallel=ALLOW_PARALLEL_CHANNELS)
    save_edges(edges, output_file_path)
    print(f"✅ Generated {len(edges)} edges saved to {output_file_path}")
