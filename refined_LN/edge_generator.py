import json
import random
import uuid
import hashlib
from itertools import combinations
from typing import List

def load_nodes(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        data = json.load(f)
        return [node['pub_key'] for node in data['nodes'] if 'pub_key' in node]

def generate_channel_id_and_point(index: int) -> (str, str):
    base = f"channel_{index}_{uuid.uuid4()}"
    channel_id = int(hashlib.sha256(base.encode()).hexdigest(), 16) % (1 << 64)
    chan_point_txid = hashlib.sha256((base + "_tx").encode()).hexdigest()
    chan_point_index = random.randint(0, 1)
    return str(channel_id), f"{chan_point_txid}:{chan_point_index}"

def generate_edges(pub_keys: List[str], num_edges: int, allow_parallel: bool = False) -> List[dict]:
    channels = []
    pair_set = set()
    
    for i in range(num_edges):
        node1, node2 = random.sample(pub_keys, 2)
        pair = tuple(sorted((node1, node2)))

        if not allow_parallel and pair in pair_set:
            continue  # skip duplicate pair if not allowing parallel

        pair_set.add(pair)

        channel_id, chan_point = generate_channel_id_and_point(i)
        capacity = str(random.randint(10000, 1000000))

        channels.append({
            "channel_id": channel_id,
            "chan_point": chan_point,
            "last_update": 0,
            "node1_pub": node1,
            "node2_pub": node2,
            "capacity": capacity,
            "node1_policy": None,
            "node2_policy": None,
            "custom_records": {}
        })
    return channels

def save_edges(edges: List[dict], output_path: str):
    with open(output_path, 'w') as f:
        json.dump({"edges": edges}, f, indent=4)

if __name__ == "__main__":
    node_file_path = "nodes_22.json"  # your input node file
    output_file_path = "edges_generated.json"
    NUM_EDGES = 80  # adjustable
    ALLOW_PARALLEL_CHANNELS = True  # toggle this for parallel channel behavior

    pub_keys = load_nodes(node_file_path)
    edges = generate_edges(pub_keys, NUM_EDGES, allow_parallel=ALLOW_PARALLEL_CHANNELS)
    save_edges(edges, output_file_path)
    print(f"Generated {len(edges)} edges saved to {output_file_path}")
