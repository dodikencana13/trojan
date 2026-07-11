import os
from web3 import Web3
from solcx import compile_source, install_solc

# --- CONFIGURATION ---
RPC_URL = "https://ethereum-sepolia.publicnode.com"
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

def deploy_contract():
    # 1. Install solc compiler
    print("Installing solc compiler...")
    install_solc("0.8.0")

    # 2. Connect to Sepolia
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Error: Could not connect to Sepolia node.")
        return

    # 3. Compile the Solidity contract
    print("Compiling GaslessRelayer.sol...")
    with open("GaslessRelayer.sol", "r") as f:
        source_code = f.read()
    
    compiled_sol = compile_source(source_code, output_values=["abi", "bin"], solc_version="0.8.0")
    contract_id = list(compiled_sol.keys())[0]
    abi = compiled_sol[contract_id]["abi"]
    bin = compiled_sol[contract_id]["bin"]

    # 4. Prepare the deployment transaction
    print(f"Preparing deployment for {ADDRESS} on Sepolia...")
    nonce = w3.eth.get_transaction_count(ADDRESS)
    
    deploy_tx = {
        'from': ADDRESS,
        'nonce': nonce,
        'gas': 2000000, 
        'gasPrice': int(w3.eth.gas_price * 1.2),
        'data': bin,
        'chainId': 11155111 # Sepolia Chain ID
    }
    print(f"Deploying with gasPrice: {deploy_tx['gasPrice']}")

    # 5. Attempt to sign and send
    try:
        signed_tx = w3.eth.account.sign_transaction(deploy_tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Contract Deployment Sent! Hash: {w3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Contract deployed at: {receipt.contractAddress}")
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")
        print("\nREASON: Even on Sepolia, the wallet needs a small amount of TEST-ETH.")
        print(f"Current Sepolia Balance: {w3.from_wei(w3.eth.get_balance(ADDRESS), 'ether')} ETH")
        print("\nFIX: Go to a Sepolia Faucet (e.g., Alchemy or Infura) and send test-ETH to your address.")

if __name__ == "__main__":
    deploy_contract()
