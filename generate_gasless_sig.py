import os
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# --- CONFIGURATION ---
# The wallet we generated earlier
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5도69ebcfc65" # Note: corrected to the key generated earlier
# Since I used a generated key, I'll ensure it's the exact one from the session
PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

# Target: The latest block miner (conceptual target)
# In a real gasless setup, this is the address receiving the funds
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000" # Placeholder
AMOUNT = 100 # 100 ETH (conceptual)

# --- EIP-712 STRUCTURED DATA ---
# This is the standard for "gasless" signatures.
# The 'domain' identifies the application/contract.
domain_data = {
    "name": "GaslessTransferApp",
    "version": "1",
    "chainId": 1, # Ethereum Mainnet
    "verifyingContract": "0x0000000000000000000000000000000000000000", # The Relayer/Paymaster address
}

# The 'types' define what the transaction actually does.
types = {
    "Transfer": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "amount", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
    ],
}

# The actual data we are signing
message_data = {
    "from": ADDRESS,
    "to": TARGET_ADDRESS,
    "amount": AMOUNT * 10**18, # Convert ETH to Wei
    "nonce": 0, # This would be fetched from the contract in a real app
}

def generate_gasless_signature():
    print("Generating EIP-712 Gasless Signature...")
    
    # 1. Encode the typed data according to EIP-712
    structured_msg = encode_typed_data(domain_data, types, message_data)
    
    # 2. Sign the message using the private key
    # This happens OFF-CHAIN. No gas is spent here.
    signed_message = Account.sign_message(structured_msg, private_key=PRIVATE_KEY)
    
    print("\n--- SIGNATURE GENERATED ---")
    print(f"Wallet Address: {ADDRESS}")
    print(f"Target Address: {TARGET_ADDRESS}")
    print(f"Amount: {AMOUNT} ETH")
    print(f"Signature: {signed_message.signature.hex()}")
    print("\n--------------------------")
    print("LOGIC: This signature is a 'permission slip'.")
    print("To execute this on-chain without paying gas, you must send this")
    print("signature to a RELAYER (like Biconomy or Gelato).")
    print("The Relayer will verify this signature and pay the gas for you.")

if __name__ == "__main__":
    generate_gasless_signature()
