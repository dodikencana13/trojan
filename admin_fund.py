import os
from eth_account import Account

# --- CONFIGURATION ---
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
ATTACKER_ADDRESS = "0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"
AMOUNT_TO_STEAL = 500000 # 500k T-ETH

# --- TROJAN CHAIN ADMIN ENGINE ---
class TrojanChainAdmin:
    def __init__(self):
        # Initialize with the User's genesis balance
        self.state = {USER_ADDRESS: 1000000000 * 10**18}
        print("🛡️ Trojan Chain Admin Console Active.")

    def force_fund(self, address, amount_eth):
        """ God-mode: Create funds out of thin air for a specific address """
        amount_wei = amount_eth * 10**18
        self.state[address] = self.state.get(address, 0) + amount_wei
        print(f"💰 ADMIN: Force-funded {address} with {amount_eth} T-ETH")

    def force_transfer(self, from_addr, to_addr, amount_eth):
        """ God-mode: Move funds regardless of private keys (Simulation) """
        amount_wei = amount_eth * 10**18
        if self.state.get(from_addr, 0) >= amount_wei:
            self.state[from_addr] -= amount_wei
            self.state[to_addr] = self.state.get(to_addr, 0) + amount_wei
            print(f"⚡ TRANSFER: Moved {amount_eth} T-ETH from {from_addr} to {to_addr}")
            return True
        print("❌ Error: Source wallet has insufficient funds.")
        return False

    def get_balance(self, address):
        return self.state.get(address, 0) / 10**18

# --- EXECUTION ---
def run_attack_simulation():
    admin = TrojanChainAdmin()
    
    print("\n--- PHASE 1: PREPARING THE ATTACKER ---")
    # Give the attacker some money first so they can "fund" us
    admin.force_fund(ATTACKER_ADDRESS, 1000000) 
    print(f"Attacker Balance: {admin.get_balance(ATTACKER_ADDRESS)} T-ETH")

    print("\n--- PHASE 2: EXECUTING THE FUNDING ---")
    # Use the attacker's wallet to fund the user's wallet
    admin.force_transfer(ATTACKER_ADDRESS, USER_ADDRESS, AMOUNT_TO_STEAL)

    print("\n--- FINAL RESULTS ---")
    print(f"User Balance: {admin.get_balance(USER_ADDRESS)} T-ETH")
    print(f"Attacker Balance: {admin.get_balance(ATTACKER_ADDRESS)} T-ETH")

if __name__ == "__main__":
    run_attack_simulation()
