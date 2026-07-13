import os
from web3 import Web3
from solcx import compile_source, install_solc

# --- PRODUCTION MAINNET CONFIGURATION ---
ETH_RPC = "https://ethereum-rpc.publicnode.com"
TROJAN_RPC = "http://localhost:5000" 
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

def deploy_real_bridge():
    # 1. Connect to Mainnet
    w3_eth = Web3(Web3.HTTPProvider(ETH_RPC))
    if not w3_eth.is_connected():
        print("❌ Error: Could not connect to Ethereum Mainnet.")
        return

    print("🚀 Starting Real Bridge Deployment to Mainnet (Chain ID: 1)...")

    # 2. Compile Bridge Contract
    try:
        install_solc("0.8.0")
        with open("contracts/BridgeContract.sol", "r") as f:
            source_code = f.read()
        
        compiled_sol = compile_source(source_code, output_values=["abi", "bin"], solc_version="0.8.0")
        contract_id = list(compiled_sol.keys())[0]
        bin = compiled_sol[contract_id]["bin"]
        print("✅ BridgeContract.sol compiled successfully.")
    except Exception as e:
        print(f"❌ Compilation Error: {e}")
        return

    # 3. Deploy to Mainnet
    nonce = w3_eth.eth.get_transaction_count(ADDRESS)
    deploy_tx = {
        'from': ADDRESS,
        'nonce': nonce,
        'gas': 3000000, # Higher gas limit for contract deployment
        'gasPrice': int(w3_eth.eth.gas_price * 1.2),
        'data': bin,
        'chainId': 1
    }

    try:
        print(f"Sending deployment transaction from {ADDRESS}...")
        signed_tx = w3_eth.eth.account.sign_transaction(deploy_tx, PRIVATE_KEY)
        tx_hash = w3_eth.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Bridge Contract Deployment Sent! Hash: {w3.to_hex(tx_hash)}")
        
        print("Waiting for Mainnet confirmation (this may take a few minutes)...")
        receipt = w3_eth.eth.wait_for_transaction_receipt(tx_hash)
        bridge_address = receipt.contractAddress
        print(f"🎉 SUCCESS! Real Bridge deployed at: {bridge_address}")
        
        # Save the address for the Relayer
        with open("bridge_address.txt", "w") as f:
            f.write(bridge_address)
            
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")
        print("\n--- CRITICAL STATUS CHECK ---")
        balance = w3_eth.eth.get_balance(ADDRESS)
        print(f"Current Wallet Balance: {w3_eth.from_wei(balance, 'ether')} ETH")
        print("Requirement: To deploy a real contract on Mainnet, you MUST have ETH in your wallet.")

if __name__ == "__main__":
    # Setup web3 globally for the print statement
    w3 = Web3(Web3.HTTPProvider(ETH_RPC))
    deploy_real_bridge()
