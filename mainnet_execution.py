import os
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from solcx import compile_source, install_solc

# --- PRODUCTION CONFIGURATION ---
RPC_URL = "https://ethereum-rpc.publicnode.com"
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000" 
AMOUNT = 0.001 

def run_mainnet_production():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Error: Could not connect to Mainnet.")
        return

    print("=== STARTING MAINNET PRODUCTION FLOW ===")
    
    # --- STEP 0: DEPLOYMENT ---
    print("\n[Step 0] Deploying GaslessRelayer to Mainnet...")
    try:
        install_solc("0.8.0")
        with open("GaslessRelayer.sol", "r") as f:
            source_code = f.read()
        
        compiled_sol = compile_source(source_code, output_values=["abi", "bin"], solc_version="0.8.0")
        contract_id = list(compiled_sol.keys())[0]
        abi = compiled_sol[contract_id]["abi"]
        bin = compiled_sol[contract_id]["bin"]

        nonce = w3.eth.get_transaction_count(ADDRESS)
        deploy_tx = {
            'from': ADDRESS,
            'nonce': nonce,
            'gas': 2000000, 
            'gasPrice': int(w3.eth.gas_price * 1.2),
            'data': bin,
            'chainId': 1
        }

        signed_deploy = w3.eth.account.sign_transaction(deploy_tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_deploy.raw_transaction)
        print(f"✅ Deployment sent! Hash: {w3.to_hex(tx_hash)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt.contractAddress
        print(f"✅ Contract Live at: {contract_address}")
    except Exception as e:
        print(f"❌ Deployment Failed: {e}")
        print("Reason: Wallet has 0 ETH. Deployment requires real ETH for gas.")
        return

    # --- STEP 1: SIGNATURE ---
    print("\n[Step 1] Generating Production Signature...")
    contract = w3.eth.contract(address=contract_address, abi=abi)
    nonce = contract.functions.nonces(ADDRESS).call()
    
    domain_data = {
        "name": "GaslessTransferApp",
        "version": "1",
        "chainId": 1,
        "verifyingContract": contract_address,
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
        "from": ADDRESS,
        "to": TARGET_ADDRESS,
        "amount": w3.to_wei(AMOUNT, 'ether'),
        "nonce": nonce,
    }
    
    structured_msg = encode_typed_data(domain_data, types, message_data)
    signed_message = Account.sign_message(structured_msg, private_key=PRIVATE_KEY)
    signature = signed_message.signature
    print(f"✅ Signature Generated: {signature.hex()[:20]}...")

    # --- STEP 2 & 3: RELAY & EXECUTE ---
    print("\n[Step 2 & 3] Relaying and Executing Transfer...")
    try:
        tx = contract.functions.executeTransfer(
            ADDRESS,
            TARGET_ADDRESS,
            w3.to_wei(AMOUNT, 'ether'),
            nonce,
            signature
        ).build_transaction({
            'from': ADDRESS,
            'nonce': w3.eth.get_transaction_count(ADDRESS),
            'gas': 200000,
            'gasPrice': int(w3.eth.gas_price * 1.2),
            'chainId': 1
        })
        
        signed_exec = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        exec_hash = w3.eth.send_raw_transaction(signed_exec.raw_transaction)
        print(f"✅ Execution sent! Hash: {w3.to_hex(exec_hash)}")
        
        receipt = w3.eth.wait_for_transaction_receipt(exec_hash)
        print(f"✅ SUCCESS: Transfer executed in block {receipt.blockNumber}!")
    except Exception as e:
        print(f"❌ Execution Failed: {e}")

if __name__ == "__main__":
    run_mainnet_production()
