import os
from web3 import Web3

# --- CONFIGURATION ---
# Public RPC for Ethereum Mainnet
RPC_URL = "https://ethereum-rpc.publicnode.com" 

# The wallet we generated earlier
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

# Amount to send (In this case, we'll use a small amount as a placeholder)
# Note: This will fail if the wallet balance is 0.
AMOUNT_TO_SEND = 0.01 

def send_to_latest_block_miner():
    # 1. Connect to the Ethereum node
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("Error: Could not connect to Ethereum node.")
        return

    print("Connected to Ethereum Mainnet.")

    # 2. Get the latest block to find the "latest block" address (the miner/fee recipient)
    try:
        latest_block = w3.eth.get_block('latest')
        # In PoS Ethereum, 'miner' usually refers to the fee recipient of the block
        target_address = latest_block['miner'] 
        block_number = latest_block['number']
        print(f"Latest Block: {block_number}")
        print(f"Target Address (Miner/Fee Recipient): {target_address}")
    except Exception as e:
        print(f"Error retrieving latest block: {e}")
        return

    # 3. Check the wallet balance
    balance = w3.eth.get_balance(ADDRESS)
    print(f"Current Wallet Balance: {w3.from_wei(balance, 'ether')} ETH")

    if balance == 0:
        print("❌ Execution stopped: Wallet balance is 0. You must fund the wallet with ETH to send a transaction.")
        return

    # 4. Build the transaction
    try:
        nonce = w3.eth.get_transaction_count(ADDRESS)
        tx = {
            'nonce': nonce,
            'to': target_address,
            'value': w3.to_wei(AMOUNT_TO_SEND, 'ether'),
            'gas': 21000, # Standard ETH transfer gas limit
            'gasPrice': w3.eth.gas_price,
            'chainId': 1
        }

        # 5. Sign the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # 6. Send the transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Transaction sent! Hash: {w3.to_hex(tx_hash)}")
        
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed in block {receipt.blockNumber}")

    except Exception as e:
        print(f"An error occurred during the transaction: {e}")

if __name__ == "__main__":
    send_to_latest_block_miner()
