import os
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# --- CONFIGURATION ---
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
USER_PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000"
GENESIS_AMOUNT = 1000000 # 1 Million ETH
TRANSFER_AMOUNT = 100 # 100 ETH

# --- THE GENESIS BLOCKCHAIN SIMULATOR ---
class GenesisBlockchain:
    def __init__(self):
        # The "State" of the blockchain: Address -> Balance (in Wei)
        self.state = {}
        self.contracts = {}
        self.nonces = {}
        print("🌐 Initializing Genesis Blockchain...")

    def create_genesis_block(self, address, amount_eth):
        print(f"🧱 Creating Genesis Block... Granting {amount_eth} ETH to {address}")
        self.state[address] = amount_eth * 10**18
        self.nonces[address] = 0
        print("✅ Genesis Block finalized.")

    def deploy_contract(self, name, contract_instance):
        # Simulate deployment by giving the contract an address
        contract_address = "0x" + os.urandom(20).hex()
        self.contracts[contract_address] = contract_instance
        print(f"🚀 Contract '{name}' deployed to {contract_address}")
        return contract_address

    def get_balance(self, address):
        return self.state.get(address, 0) / 10**18

# --- THE GASLESS RELAYER SMART CONTRACT LOGIC ---
class GaslessRelayerContract:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.address = None # Set upon deployment
        self.domain_separator = "GASLESS_DOMAIN_SEP" # Simulated separator

    def execute_transfer(self, from_addr, to_addr, amount_wei, nonce, signature):
        print("\n[Contract] Verifying gasless request...")
        
        # 1. Verify Nonce
        if self.blockchain.nonces.get(from_addr, 0) != nonce:
            print("❌ Invalid Nonce")
            return False

        # 2. Verify Signature (Real Cryptography)
        # We simulate the EIP-712 hash the contract would compute
        domain_data = {
            "name": "GaslessTransferApp",
            "version": "1",
            "chainId": 1,
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
            print(f"❌ Invalid Signature. Recovered: {recovered_addr}")
            return False
        
        print("✅ Signature Verified. Executing transfer...")

        # 3. Perform the Transfer
        if self.blockchain.state.get(from_addr, 0) >= amount_wei:
            self.blockchain.state[from_addr] -= amount_wei
            self.blockchain.state[to_addr] = self.blockchain.state.get(to_addr, 0) + amount_wei
            self.blockchain.nonces[from_addr] += 1
            print(f"✅ Transfer Successful: {amount_wei / 10**18} ETH moved.")
            return True
        else:
            print("❌ Insufficient Funds in Wallet")
            return False

# --- THE FULL FLOW ---
def run_genesis_test():
    # 1. Start Blockchain and Genesis
    chain = GenesisBlockchain()
    chain.create_genesis_block(USER_ADDRESS, GENESIS_AMOUNT)
    
    # 2. Deploy Contract
    relayer_logic = GaslessRelayerContract(chain)
    contract_addr = chain.deploy_contract("GaslessRelayer", relayer_logic)
    relayer_logic.address = contract_addr
    
    print(f"\nInitial Balance: {chain.get_balance(USER_ADDRESS)} ETH")

    # 3. Generate Off-Chain Signature (User action)
    print("\n--- USER: Generating Signature ---")
    domain_data = {
        "name": "GaslessTransferApp",
        "version": "1",
        "chainId": 1,
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

    # 4. Relayer submits signature to contract (Relayer action)
    print("\n--- RELAYER: Submitting to Blockchain ---")
    success = relayer_logic.execute_transfer(
        USER_ADDRESS, 
        TARGET_ADDRESS, 
        TRANSFER_AMOUNT * 10**18, 
        0, 
        signature
    )

    if success:
        print("\n--- FINAL STATE ---")
        print(f"User Balance: {chain.get_balance(USER_ADDRESS)} ETH")
        print(f"Target Balance: {chain.get_balance(TARGET_ADDRESS)} ETH")
    else:
        print("Flow failed.")

if __name__ == "__main__":
    run_genesis_test()
