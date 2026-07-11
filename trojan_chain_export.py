import os
import json
from datetime import datetime
from eth_account import Account
from eth_account.messages import encode_typed_data

# --- TROJAN CHAIN CONFIGURATION ---
CHAIN_NAME = "Trojan Chain"
CHAIN_ID = 1303
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
USER_PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000"
GENESIS_AMOUNT = 1000000000 # 1 Billion Trojan ETH

class TrojanChain:
    def __init__(self):
        self.name = CHAIN_NAME
        self.chain_id = CHAIN_ID
        self.state = {}
        self.contracts = {}
        self.nonces = {}
        self.transactions = [] # List of all txs
        self.blocks = []       # List of blocks
        print(f"🚀 Initializing {self.name}...")

    def initialize_genesis(self, address, amount_eth):
        # Genesis Block
        block = {
            "number": 0,
            "timestamp": datetime.now().isoformat(),
            "transactions": [],
            "hash": "0x0000000000000000000000000000000000000000000000000000000000000000"
        }
        self.state[address] = amount_eth * 10**18
        self.nonces[address] = 0
        self.blocks.append(block)
        print(f"🧱 Genesis Block Created. {amount_eth} T-ETH granted to {address}")

    def deploy_contract(self, name, contract_instance):
        contract_address = "0x" + os.urandom(20).hex()
        self.contracts[contract_address] = contract_instance
        
        tx = {
            "hash": "0x" + os.urandom(32).hex(),
            "from": "0x0000000000000000000000000000000000000000",
            "to": contract_address,
            "value": 0,
            "type": "Contract Deployment",
            "timestamp": datetime.now().isoformat(),
            "details": f"Deployed {name}"
        }
        self.transactions.append(tx)
        self._mine_block()
        return contract_address

    def _mine_block(self):
        # Simple block mining simulation
        block_num = len(self.blocks)
        block = {
            "number": block_num,
            "timestamp": datetime.now().isoformat(),
            "transactions": [tx['hash'] for tx in self.transactions if tx['timestamp'] >= self.blocks[-1]['timestamp'] if self.blocks],
            "hash": "0x" + os.urandom(32).hex()
        }
        self.blocks.append(block)

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce, signature, relayer_addr):
        # Logic for transfer
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
                "timestamp": datetime.now().isoformat(),
                "details": f"Gasless transfer via Relayer {relayer_addr}"
            }
            self.transactions.append(tx)
            self._mine_block()
            return True, tx['hash']
        return False, None

    def export_state(self):
        return {
            "chain_name": self.name,
            "chain_id": self.chain_id,
            "balances": {addr: bal / 10**18 for addr, bal in self.state.items()},
            "transactions": self.transactions,
            "blocks": self.blocks,
            "contracts": list(self.contracts.keys())
        }

# --- THE GASLESS RELAYER ---
class TrojanGaslessRelayer:
    def __init__(self, chain):
        self.chain = chain
        self.address = None

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce, signature):
        domain_data = {"name": "TrojanGaslessApp", "version": "1", "chainId": self.chain.chain_id, "verifyingContract": self.address}
        types = {"Transfer": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "nonce", "type": "uint256"}]}
        message_data = {"from": from_addr, "to": to_addr, "amount": amount_wei, "nonce": nonce}
        
        structured_msg = encode_typed_data(domain_data, types, message_data)
        recovered_addr = Account.recover_message(structured_msg, signature=signature)
        
        if recovered_addr.lower() == from_addr.lower():
            success, tx_hash = self.chain.execute_transfer(from_addr, to_addr, amount_wei, nonce, signature, self.address)
            return success, tx_hash
        return False, None

# --- MAIN EXECUTION ---
def launch_and_export():
    trojan = TrojanChain()
    trojan.initialize_genesis(USER_ADDRESS, GENESIS_AMOUNT)
    
    relayer = TrojanGaslessRelayer(trojan)
    contract_addr = trojan.deploy_contract("TrojanGaslessRelayer", relayer)
    relayer.address = contract_addr
    
    # Perform some transactions to populate the explorer
    # Tx 1: Big transfer to target
    domain_data = {"name": "TrojanGaslessApp", "version": "1", "chainId": CHAIN_ID, "verifyingContract": contract_addr}
    types = {"Transfer": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "nonce", "type": "uint256"}]}
    
    # Transfer 1M
    msg1 = {"from": USER_ADDRESS, "to": TARGET_ADDRESS, "amount": 1000000 * 10**18, "nonce": 0}
    sig1 = Account.sign_message(encode_typed_data(domain_data, types, msg1), private_key=USER_PRIVATE_KEY).signature
    relayer.execute_transfer(USER_ADDRESS, TARGET_ADDRESS, 1000000 * 10**18, 0, sig1)

    # Transfer 50k to another random address
    RANDOM_ADDR = "0x1234567890123456789012345678901234567890"
    msg2 = {"from": USER_ADDRESS, "to": RANDOM_ADDR, "amount": 50000 * 10**18, "nonce": 1}
    sig2 = Account.sign_message(encode_typed_data(domain_data, types, msg2), private_key=USER_PRIVATE_KEY).signature
    relayer.execute_transfer(USER_ADDRESS, RANDOM_ADDR, 50000 * 10**18, 1, sig2)

    # Export to JSON for the explorer
    with open("chain_state.json", "w") as f:
        json.dump(trojan.export_state(), f, indent=4)
    print("\n✅ Trojan Chain state exported to chain_state.json")

if __name__ == "__main__":
    launch_and_export()
