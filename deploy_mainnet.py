import os
from web3 import Web3
from solcx import compile_source

# --- CONFIGURATION ---
RPC_URL = "https://ethereum-rpc.publicnode.com"
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

def deploy_contract():
    # 1. Connect to Ethereum
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Error: Could not connect to node.")
        return

    # 2. Compile the Solidity contract
    print("Compiling GaslessRelayer.sol...")
    with open("GaslessRelayer.sol", "r") as f:
        source_code = f.read()
    
    compiled_sol = compile_source(source_code, output_values=["abi", "bin"])
    contract_id = list(compiled_sol.keys())[0]
    abi = compiled_sol[contract_id]["abi"]
    bin = compiled_sol[contract_id]["bin"]

    # 3. Prepare the deployment transaction
    print(f"Preparing deployment for {ADDRESS}...")
    nonce = w3.eth.get_transaction_count(ADDRESS)
    
    # Estimate gas for deployment
    deploy_tx = {
        'from': ADDRESS,
        'nonce': nonce,
        'gas': 2000000, 
        'gasPrice': w3.eth.gas_price,
        'data': bin,
        'chainId': 1
    }

    # 4. Attempt to sign and send
    try:
        # This will FAIL if balance is 0
        signed_tx = w3.eth.account.sign_transaction(deploy_tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Contract Deployment Sent! Hash: {w3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Contract deployed at: {receipt.contractAddress}")
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")
        print("\nREASON: To deploy to mainnet, the wallet MUST have real ETH to pay the gas fee.")
        print(f"Current Balance: {w3.from_wei(w3.eth.get_balance(ADDRESS), 'ether')} ETH")

if __name__ == "__main__":
    # Note: solcx requires solc to be installed
    try:
        import solcx
        deploy_contract()
    except ImportError:
        print("Error: solcx library not installed. Run 'pip install py-solc-x'")
