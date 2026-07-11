import os
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# --- TROJAN CHAIN CONFIGURATION ---
CHAIN_NAME = "Trojan Chain"
CHAIN_ID = 1303
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
USER_PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000"
GENESIS_AMOUNT = 1000000000 # 1 Billion Trojan ETH
TRANSFER_AMOUNT = 1000000 # 1 Million Trojan ETH

# --- THE TROJAN CHAIN ENGINE ---
class TrojanChain:
    def __init__(self):
        self.name = CHAIN_NAME
        self.chain_id = CHAIN_ID
        self.state = {}
        self.contracts = {}
        self.nonces = {}
        print(f"🚀 Initializing {self.name}...")
        print(f"⛓️ Chain ID: {self.chain_id}")

    def initialize_genesis(self, address, amount_eth):
        print(f"🧱 Mining Genesis Block... Granting {amount_eth} Trojan ETH to {address}")
        self.state[address] = amount_eth * 10**18
        self.nonces[address] = 0
        print(f"✅ {self.name} is now LIVE.")

    def deploy_contract(self, name, contract_instance):
        contract_address = "0x" + os.urandom(20).hex()
        self.contracts[contract_address] = contract_instance
        print(f"📦 Contract '{name}' deployed to {contract_address} on {self.name}")
        return contract_address

    def get_balance(self, address):
        return self.state.get(address, 0) / 10**18

# --- THE GASLESS RELAYER (TROJAN VERSION) ---
class TrojanGaslessRelayer:
    def __init__(self, chain):
        self.chain = chain
        self.address = None

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce, signature):
        print(f"\n[TrojanRelayer] Processing request on Chain {self.chain.chain_id}...")
        
        if self.chain.nonces.get(from_addr, 0) != nonce:
            print("❌ Nonce Mismatch")
            return False

        # EIP-712 Logic tuned for Trojan Chain
        domain_data = {
            "name": "TrojanGaslessApp",
            "version": "1",
            "chainId": self.chain.chain_id,
            "verifyingContract": self.address,
        }
        types = {
            "Transfer": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
            ],
        }
        message_data = {
            "from": from_addr,
            "to": to_addr,
            "amount": amount_wei,
            "nonce": nonce,
        }
        
        structured_msg = encode_typed_data(domain_data, types, message_data)
        recovered_addr = Account.recover_message(structured_msg, signature=signature)
        
        if recovered_addr.lower() != from_addr.lower():
            print(f"❌ Invalid Signature for Trojan Chain")
            return False
        
        if self.chain.state.get(from_addr, 0) >= amount_wei:
            self.chain.state[from_addr] -= amount_wei
            self.chain.state[to_addr] = self.chain.state.get(to_addr, 0) + amount_wei
            self.chain.nonces[from_addr] += 1
            print(f"✅ Trojan Transfer Successful: {amount_wei / 10**18} T-ETH moved.")
            return True
        else:
            print("❌ Insufficient Trojan ETH")
            return False

# --- RUNNING THE TROJAN CHAIN ---
def launch_trojan_ecosystem():
    # 1. Initialize the new chain
    trojan = TrojanChain()
    trojan.initialize_genesis(USER_ADDRESS, GENESIS_AMOUNT)
    
    # 2. Deploy the relayer
    relayer = TrojanGaslessRelayer(trojan)
    contract_addr = trojan.deploy_contract("TrojanGaslessRelayer", relayer)
    relayer.address = contract_addr
    
    print(f"\nYour balance on Trojan Chain: {trojan.get_balance(USER_ADDRESS)} T-ETH")

    # 3. Execute a massive gasless transfer
    print("\n--- AUTHORIZING TRANSFER ---")
    domain_data = {
        "name": "TrojanGaslessApp",
        "version": "1",
        "chainId": CHAIN_ID,
        "verifyingContract": contract_addr,
    }
    types = {
        "Transfer": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
        ],
    }
    message_data = {
        "from": USER_ADDRESS,
        "to": TARGET_ADDRESS,
        "amount": TRANSFER_AMOUNT * 10**18,
        "nonce": 0,
    }
    
    structured_msg = encode_typed_data(domain_data, types, message_data)
    signed_msg = Account.sign_message(structured_msg, private_key=USER_PRIVATE_KEY)
    signature = signed_msg.signature

    print("\n--- RELAYING TO TROJAN CHAIN ---")
    success = relayer.execute_transfer(
        USER_ADDRESS, 
        TARGET_ADDRESS, 
        TRANSFER_AMOUNT * 10**18, 
        0, 
        signature
    )

    if success:
        print("\n--- FINAL TROJAN STATE ---")
        print(f"User Balance: {trojan.get_balance(USER_ADDRESS)} T-ETH")
        print(f"Target Balance: {trojan.get_balance(TARGET_ADDRESS)} T-ETH")

if __name__ == "__main__":
    launch_trojan_ecosystem()
