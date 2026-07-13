import requests
import json
import time

RPC_URL = "http://localhost:5000"
SENDER = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
RECEIVER = "0x7777777777777777777777777777777777777777"
AMOUNT = 100.0

def call_rpc(method, params=[]):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload).json()
    if "error" in response:
        raise Exception(response["error"]["message"])
    return response["result"]

def test_wallet_flow():
    print("--- 📱 TROJAN WALLET SIMULATION ---")
    
    # 1. Check Initial Balance
    bal_start = int(call_rpc("eth_getBalance", [SENDER]), 16) / 10**18
    print(f"SENDER Balance: {bal_start} T-ETH")
    
    # 2. Send T-ETH
    print(f"\nSending {AMOUNT} T-ETH to {RECEIVER}...")
    tx_hash = call_rpc("trojan_transfer", [SENDER, RECEIVER, AMOUNT])
    print(f"✅ Transaction Sent! Hash: {tx_hash}")
    
    # 3. Verify Receive
    bal_end_sender = int(call_rpc("eth_getBalance", [SENDER]), 16) / 10**18
    bal_end_receiver = int(call_rpc("eth_getBalance", [RECEIVER]), 16) / 10**18
    
    print(f"\n--- FINAL RESULTS ---")
    print(f"SENDER Balance: {bal_end_sender} T-ETH")
    print(f"RECEIVER Balance: {bal_end_receiver} T-ETH")
    
    if bal_end_receiver == AMOUNT:
        print("\n🎉 SUCCESS: Send and Receive verified!")
    else:
        print("\n❌ FAILED: Balance mismatch.")

if __name__ == "__main__":
    test_wallet_flow()
