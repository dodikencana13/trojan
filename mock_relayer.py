import os
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

# --- SETUP DATA (Matching the previous script) ---
# The User's Wallet
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
USER_PRIVATE_KEY = "e62fecde673c65472da447b4996b835dfe37e4393583153d5d075d069ebcfc65"

# The Signature generated in the previous step
SIGNATURE = "dd7dac7cdf304c2ec1f43f6665c077da92a5ee93d62ab85c5d653d3d323e650b1e9bb9309e93783e0104776f7d7bc315e9bcff5710946e7654a30b4eeb4e28f81b"

# The original message data
TARGET_ADDRESS = "0x0000000000000000000000000000000000000000"
AMOUNT = 100

domain_data = {
    "name": "GaslessTransferApp",
    "version": "1",
    "chainId": 1,
    "verifyingContract": "0x0000000000000000000000000000000000000000",
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
    "amount": AMOUNT * 10**18,
    "nonce": 0,
}

# --- MOCK RELAYER LOGIC ---
class MockRelayer:
    def __init__(self):
        # The Relayer has its own fund to pay for gas
        self.relayer_balance = 1.0 # 1 ETH for gas fees
        self.blockchain_state = {
            USER_ADDRESS: 100 * 10**18, # Simulate that the user actually has 100 ETH
            TARGET_ADDRESS: 0
        }
        print("Mock Relayer Initialized.")
        print(f"Relayer Gas Fund: {self.relayer_balance} ETH")

    def process_gasless_tx(self, signature, domain, types, message):
        print("\n--- RELAYER PROCESSING START ---")
        
        # 1. Verify the signature
        # In a real relayer, the smart contract on-chain does this.
        print("Step 1: Verifying Signature...")
        structured_msg = encode_typed_data(domain, types, message)
        
        try:
            # Recover the address that signed the message
            recovered_address = Account.recover_message(structured_msg, signature=SIGNATURE)
            print(f"Recovered Address: {recovered_address}")
            
            if recovered_address.lower() == message['from'].lower():
                print("✅ Signature Valid: User authorized this transaction.")
            else:
                print("❌ Signature Invalid: Address mismatch.")
                return False
        except Exception as e:
            print(f"Error during verification: {e}")
            return False

        # 2. Pay the Gas
        print("Step 2: Paying Gas Fee...")
        gas_cost = 0.001 # Simulated gas cost
        if self.relayer_balance >= gas_cost:
            self.relayer_balance -= gas_cost
            print(f"✅ Gas Paid. Relayer Balance remaining: {self.relayer_balance} ETH")
        else:
            print("❌ Relayer out of funds to pay gas.")
            return False

        # 3. Execute the transfer on the 'blockchain'
        print("Step 3: Executing Transfer on Blockchain...")
        sender = message['from']
        receiver = message['to']
        value = message['amount']

        if self.blockchain_state.get(sender, 0) >= value:
            self.blockchain_state[sender] -= value
            self.blockchain_state[receiver] = self.blockchain_state.get(receiver, 0) + value
            print(f"✅ Transfer Complete: {value / 10**18} ETH moved from {sender} to {receiver}")
        else:
            print("❌ Transaction Failed: Sender has insufficient balance.")
            return False

        print("--- RELAYER PROCESSING SUCCESS ---")
        return True

if __name__ == "__main__":
    relayer = MockRelayer()
    success = relayer.process_gasless_tx(SIGNATURE, domain_data, types, message_data)
    
    if success:
        print(f"\nFinal User Balance: {relayer.blockchain_state[USER_ADDRESS] / 10**18} ETH")
        print(f"Final Target Balance: {relayer.blockchain_state[TARGET_ADDRESS] / 10**18} ETH")
    else:
        print("\nTransaction failed to process.")
