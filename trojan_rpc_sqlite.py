import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

# --- TROJAN CHAIN CONFIGURATION ---
CHAIN_ID = 1303
DB_FILE = "trojan_chain.db"

class TrojanSQLiteChain:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._setup_db()

    def _setup_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS balances (address TEXT PRIMARY KEY, balance TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS nonces (address TEXT PRIMARY KEY, nonce INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS transactions (hash TEXT PRIMARY KEY, from_addr TEXT, to_addr TEXT, value REAL, type TEXT, timestamp TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS blocks (number INTEGER PRIMARY KEY, timestamp TEXT, hash TEXT)")
        self.conn.commit()

        self.cursor.execute("SELECT count(*) FROM blocks")
        if self.cursor.fetchone()[0] == 0:
            genesis_addr = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
            # Store as string to avoid SQLite overflow
            amount_wei = str(1000000000 * 10**18)
            self.cursor.execute("INSERT INTO balances (address, balance) VALUES (?, ?)", (genesis_addr, amount_wei))
            self.cursor.execute("INSERT INTO nonces (address, nonce) VALUES (?, ?)", (genesis_addr, 0))
            self.cursor.execute("INSERT INTO blocks (number, timestamp, hash) VALUES (?, ?, ?)", 
                                (0, datetime.utcnow().isoformat(), "0x" + "0"*64))
            self.conn.commit()

    def get_balance(self, address):
        self.cursor.execute("SELECT balance FROM balances WHERE address = ?", (address,))
        row = self.cursor.fetchone()
        return int(row[0]) if row else 0

    def transfer(self, from_addr, to_addr, amount_wei):
        bal = self.get_balance(from_addr)
        if bal >= amount_wei:
            # Update sender balance
            new_bal_from = str(bal - amount_wei)
            self.cursor.execute("UPDATE balances SET balance = ? WHERE address = ?", (new_bal_from, from_addr))
            
            # Update receiver balance
            recv_bal = self.get_balance(to_addr)
            new_bal_to = str(recv_bal + amount_wei)
            self.cursor.execute("INSERT OR REPLACE INTO balances (address, balance) VALUES (?, ?)", (to_addr, new_bal_to))
            
            self.cursor.execute("UPDATE nonces SET nonce = nonce + 1 WHERE address = ?", (from_addr,))
            
            tx_hash = "0x" + os.urandom(32).hex()
            self.cursor.execute("INSERT INTO transactions (hash, from_addr, to_addr, value, type, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                (tx_hash, from_addr, to_addr, amount_wei / 10**18, "Transfer", datetime.utcnow().isoformat()))
            
            self.cursor.execute("SELECT MAX(number) FROM blocks")
            last_num = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO blocks (number, timestamp, hash) VALUES (?, ?, ?)", 
                                (last_num + 1, datetime.utcnow().isoformat(), "0x" + os.urandom(32).hex()))
            self.conn.commit()
            return True, tx_hash
        return False, None

app = Flask(__name__)
chain = TrojanSQLiteChain()

@app.route('/', methods=['POST'])
def rpc_endpoint():
    data = request.get_json()
    method = data.get("method")
    params = data.get("params", [])
    req_id = data.get("id")

    if method == "eth_getBalance":
        address = params[0]
        balance = chain.get_balance(address)
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(balance)})

    elif method == "eth_blockNumber":
        chain.cursor.execute("SELECT MAX(number) FROM blocks")
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(chain.cursor.fetchone()[0])})

    elif method == "eth_chainId":
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": hex(CHAIN_ID)})

    elif method == "trojan_transfer":
        from_addr = params[0]
        to_addr = params[1]
        amount_eth = params[2]
        amount_wei = int(amount_eth * 10**18)
        success, tx_hash = chain.transfer(from_addr, to_addr, amount_wei)
        if success:
            return jsonify({"jsonrpc": "2.0", "id": req_id, "result": tx_hash})
        return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": "Insufficient funds"}})

    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
