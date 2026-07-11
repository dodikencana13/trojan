import json
from flask import Flask, request, jsonify
from eth_account import Account
from eth_account.messages import encode_typed_data
import os
from datetime import datetime

# --- TROJAN CHAIN CORE ---
class TrojanChain:
    def __init__(self):
        self.name = "Trojan Chain"
        self.chain_id = 1303
        self.state = {"0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB": 1000000000 * 10**18}
        self.contracts = {}
        self.nonces = {"0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB": 0}
        self.transactions = []
        self.blocks = []
        self._initialize_genesis()

    def _initialize_genesis(self):
        self.blocks.append({
            "number": 0,
            "timestamp": datetime.now().isoformat(),
            "transactions": [],
            "hash": "0x" + "0"*64
        })

    def deploy_contract(self, name):
        addr = "0x" + os.urandom(20).hex()
        self.contracts[addr] = name
        tx = {
            "hash": "0x" + os.urandom(32).hex(),
            "from": "0x0000000000000000000000000000000000000000",
            "to": addr,
            "value": 0,
            "type": "Contract Deployment",
            "timestamp": datetime.now().isoformat()
        }
        self.transactions.append(tx)
        self._mine_block()
        return addr

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce, signature):
        # Simplified verification for RPC demo
        if self.state.get(from_addr, 0) >= amount_wei:
            self.state[from_addr] -= amount_wei
            self.state[to_addr] = self.state.get(to_addr, 0) + amount_wei
            self.nonces[from_addr] = self.nonces.get(from_addr, 0) + 1
            tx = {
                "hash": "0x" + os.urandom(32).hex(),
                "from": from_addr,
                "to": to_addr,
                "value": amount_wei / 10**18,
                "type": "Transfer",
                "timestamp": datetime.now().isoformat()
            }
            self.transactions.append(tx)
            self._mine_block()
            return True, tx['hash']
        return False, None

    def _mine_block(self):
        block_num = len(self.blocks)
        self.blocks.append({
            "number": block_num,
            "timestamp": datetime.now().isoformat(),
            "transactions": [tx['hash'] for tx in self.transactions[-1:]],
            "hash": "0x" + os.urandom(32).hex()
        })

# --- RPC SERVER ---
app = Flask(__name__)
chain = TrojanChain()
# Deploy a relayer contract on start
RELAYER_ADDR = chain.deploy_contract("TrojanGaslessRelayer")

@app.route('/', methods=['POST'])
def rpc_endpoint():
    data = request.get_json()
    method = data.get("method")
    params = data.get("params", [])
    req_id = data.get("id")

    if method == "eth_getBalance":
        address = params[0]
        balance = chain.state.get(address, 0)
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(balance)})

    elif method == "eth_blockNumber":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(len(chain.blocks)-1)})

    elif method == "eth_chainId":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(chain.chain_id)})

    elif method == "eth_getTransactionByHash":
        tx_hash = params[0]
        tx = next((t for t in chain.transactions if t['hash'] == tx_hash), None)
        if tx:
            return jsonify({"jsonrpc": "2.0", "id": req_id, "result": tx})
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": None})

    elif method == "eth_getLogs":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": chain.transactions})

    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})

if __name__ == "__main__":
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000)
