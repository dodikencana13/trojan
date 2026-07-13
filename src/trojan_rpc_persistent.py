import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

# --- TROJAN CHAIN PRODUCTION CONFIGURATION ---
CHAIN_NAME = "Trojan Chain"
CHAIN_ID = 1303
# User will set this in their environment variables on Render/Railway/etc.
# Example: "mongodb+srv://user:pass@cluster.mongodb.net/trojan_chain?retryWrites=true&w=majority"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/") 

# --- PERSISTENT BLOCKCHAIN ENGINE ---
class TrojanPersistentChain:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["trojan_chain_db"]
        
        # Collections
        self.balances = self.db["balances"]
        self.nonces = self.db["nonces"]
        self.transactions = self.db["transactions"]
        self.blocks = self.db["blocks"]
        self.contracts = self.db["contracts"]
        
        print(f"🌐 Connecting to Persistent Storage for {CHAIN_NAME}...")
        self._ensure_genesis()

    def _ensure_genesis(self):
        # Only create genesis if the chain is empty
        if self.blocks.count_documents({}) == 0:
            print("🧱 No existing chain found. Mining Genesis Block...")
            genesis_address = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
            amount_wei = 1000000000 * 10**18
            
            # Set initial balance
            self.balances.update_one(
                {"address": genesis_address},
                {"$set": {"balance": amount_wei}},
                upsert=True
            )
            # Set initial nonce
            self.nonces.update_one(
                {"address": genesis_address},
                {"$set": {"nonce": 0}},
                upsert=True
            )
            # Create Genesis Block
            self.blocks.insert_one({
                "number": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "transactions": [],
                "hash": "0x" + "0"*64
            })
            print(f"✅ Genesis finalized. {amount_wei / 10**18} T-ETH granted to {genesis_address}")
        else:
            print("✅ Existing chain detected. Loading state from database...")

    def get_balance(self, address):
        user = self.balances.find_one({"address": address})
        return user["balance"] if user else 0

    def get_nonce(self, address):
        user = self.nonces.find_one({"address": address})
        return user["nonce"] if user else 0

    def deploy_contract(self, name):
        addr = "0x" + os.urandom(20).hex()
        self.contracts.insert_one({"address": addr, "name": name})
        
        tx = {
            "hash": "0x" + os.urandom(32).hex(),
            "from": "0x0000000000000000000000000000000000000000",
            "to": addr,
            "value": 0,
            "type": "Contract Deployment",
            "timestamp": datetime.utcnow().isoformat(),
            "details": f"Deployed {name}"
        }
        self.transactions.insert_one(tx)
        self._mine_block()
        return addr

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce):
        # Atomic balance check and update
        current_bal = self.get_balance(from_addr)
        if current_bal >= amount_wei:
            # Deduct from sender
            self.balances.update_one({"address": from_addr}, {"$inc": {"balance": -amount_wei}})
            # Add to receiver
            self.balances.update_one({"address": to_addr}, {"$inc": {"balance": amount_wei}}, upsert=True)
            # Increment nonce
            self.nonces.update_one({"address": from_addr}, {"$inc": {"nonce": 1}}, upsert=True)
            
            tx = {
                "hash": "0x" + os.urandom(32).hex(),
                "from": from_addr,
                "to": to_addr,
                "value": amount_wei / 10**18,
                "type": "Transfer",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.transactions.insert_one(tx)
            self._mine_block()
            return True, tx["hash"]
        return False, None

    def _mine_block(self):
        last_block = self.blocks.find_one({"number": {"$exists": True}}, sort=[("number", -1)])
        block_num = (last_block["number"] + 1) if last_block else 0
        
        self.blocks.insert_one({
            "number": block_num,
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": [tx["hash"] for tx in self.transactions[-1:]],
            "hash": "0x" + os.urandom(32).hex()
        })

# --- RPC SERVER ---
app = Flask(__name__)
chain = TrojanPersistentChain(MONGO_URI)
RELAYER_ADDR = chain.deploy_contract("TrojanGaslessRelayer")

@app.route('/', methods=['POST'])
def rpc_endpoint():
    data = request.get_json()
    method = data.get("method")
    params = data.get("params", [])
    req_id = data.get("id")

    if method == "eth_getBalance":
        address = params[0]
        balance = chain.get_balance(address)
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(int(balance))})

    elif method == "eth_blockNumber":
        count = chain.blocks.count_documents({})
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(count - 1)})

    elif method == "eth_chainId":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(CHAIN_ID)})

    elif method == "eth_getTransactionByHash":
        tx_hash = params[0]
        tx = self.transactions.find_one({"hash": tx_hash}) if 'self' in locals() else chain.transactions.find_one({"hash": tx_hash})
        if tx:
            tx['_id'] = str(tx['_id']) # Convert ObjectId to string for JSON
            return jsonify({"jsonrpc": "2.0", "id": req_id, "result": tx})
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": None})

    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
