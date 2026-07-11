import os
from web3 import Web3

# --- CONFIGURATION ---
# Replace with your Infura or Alchemy URL
RPC_URL = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID" 
# Replace with the contract address you want to fund
CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000" 
# Your private key (Keep this secret! Use environment variables in production)
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "YOUR_PRIVATE_KEY")
# The amount of ETH to send (in Ether)
AMOUNT_TO_FUND = 0.1 

# Minimal ABI for a contract with a 'fund' function
# If the function requires arguments, you'll need to update this ABI.
ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "fund",
        "outputs": [],
        "payable": True,
        "type": "function",
    },
]

def call_fund_function():
    # Connect to Ethereum node
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("Error: Could not connect to Ethereum node.")
        return

    # Initialize contract
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    
    # Get the account address from the private key
    account = w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    
    print(f"Sending {AMOUNT_TO_FUND} ETH to contract {CONTRACT_ADDRESS} from {address}...")

    # Build the transaction
    # We assume the 'fund' function is payable and takes no arguments
    tx = contract.functions.fund().build_transaction({
        'from': address,
        'value': w3.to_wei(AMOUNT_TO_FUND, 'ether'),
        'gas': 200000, # Estimate gas or use w3.eth.estimate_gas
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(address),
    })

    # Sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    # Send the transaction
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent! Hash: {w3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed in block {receipt.blockNumber}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if PRIVATE_KEY == "YOUR_PRIVATE_KEY" or CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000":
        print("Please update the configuration in fund_mainnet.py with your actual RPC_URL, CONTRACT_ADDRESS, and PRIVATE_KEY.")
    else:
        call_fund_function()
