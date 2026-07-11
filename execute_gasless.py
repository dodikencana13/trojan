import os
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data

# --- CONFIGURATION ---
RPC_URL = "https://ethereum-sepolia.publicnode.com"
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
CONTRACT_ADDRESS = "0x3a07d65671F2ed313Cf53a10600F88c83bB63754"
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000" # Zero address for test
AMOUNT = 0.001 # Small amount of Sepolia ETH

# Minimal ABI for the GaslessRelayer contract
ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "nonce", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "name": "executeTransfer",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "DOMAIN_SEPARATOR",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "nonces",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

def run_full_gasless_flow():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    
    print("--- STEP 1: GENERATING OFF-CHAIN SIGNATURE ---")
    # Fetch current domain separator and nonce from the live contract
    domain_sep = contract.functions.DOMAIN_SEPARATOR().call()
    nonce = contract.functions.nonces(USER_ADDRESS).call()
    
    domain_data = {
        "name": "GaslessTransferApp",
        "version": "1",
        "chainId": 11155111, # Sepolia
        "verifyingContract": CONTRACT_ADDRESS,
    }
    
    # We must use the domain separator from the contract for the signature to be valid
    # However, encode_typed_data creates its own. To be precise, we can sign the 
    # exact hash the contract expects.
    
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
        "amount": w3.to_wei(AMOUNT, 'ether'),
        "nonce": nonce,
    }
    
    structured_msg = encode_typed_data(domain_data, types, message_data)
    signed_message = Account.sign_message(structured_msg, private_key=PRIVATE_KEY)
    signature = signed_message.signature
    
    print(f"Signature Generated: {signature.hex()[:20]}...")

    print("\n--- STEP 2 & 3: RELAYING TO MAINNET AND EXECUTING ---")
    # Now the "Relayer" (using the same key for this test) calls the contract
    try:
        # We are calling executeTransfer. The Relayer pays the gas.
        tx = contract.functions.executeTransfer(
            USER_ADDRESS,
            TARGET_ADDRESS,
            w3.to_wei(AMOUNT, 'ether'),
            nonce,
            signature
        ).build_transaction({
            'from': USER_ADDRESS, # Relayer address
            'nonce': w3.eth.get_transaction_count(USER_ADDRESS),
            'gas': 200000,
            'gasPrice': int(w3.eth.gas_price * 1.2),
            'chainId': 11155111
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Transaction sent! Hash: {w3.to_hex(tx_hash)}")
        
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Transfer Executed in block {receipt.blockNumber}!")
        print(f"Funds of {AMOUNT} ETH moved from {USER_ADDRESS} to {TARGET_ADDRESS}")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    run_full_gasless_flow()
