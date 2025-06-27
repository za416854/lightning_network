import hashlib
import time

# Step 1: Charlie 建立 preimage 與 hash
preimage = "banana123"
hash_value = hashlib.sha256(preimage.encode()).hexdigest()
print(f"[Charlie] Generated hash: {hash_value}")

# Step 2: Alice 與 Bob 建立 HTLC
alice_htlc = {
    "hash": hash_value,
    "amount": 1,  # 1 BTC (模擬用)
    "timeout": time.time() + 30  # 30 秒內有效
}
print("[Alice → Bob] HTLC established")

# Step 3: Bob 與 Charlie 建立 HTLC
bob_htlc = {
    "hash": hash_value,
    "amount": 1,
    "timeout": time.time() + 15  # 比 Alice 短，確保 Bob 有時間回頭解鎖
}
print("[Bob → Charlie] HTLC established")

# Step 4: Charlie 使用 preimage 解鎖
def claim_funds(htlc, provided_preimage, current_time):
    computed_hash = hashlib.sha256(provided_preimage.encode()).hexdigest()
    if computed_hash == htlc["hash"] and current_time < htlc["timeout"]:
        return True
    return False

# Charlie 解鎖 Bob 的 HTLC
if claim_funds(bob_htlc, preimage, time.time()):
    print("[Charlie] Claimed funds from Bob")
    # Bob 現在知道 preimage，回去解鎖 Alice 給他的 HTLC
    if claim_funds(alice_htlc, preimage, time.time()):
        print("[Bob] Claimed funds from Alice")
    else:
        print("[Bob] Failed to claim funds from Alice")
else:
    print("[Charlie] Failed to claim funds from Bob")

