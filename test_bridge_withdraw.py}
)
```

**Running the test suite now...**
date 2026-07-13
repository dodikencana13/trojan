import os
from eth_account import Account

# --- CONFIGURATION ---
USER_ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"
ATTACKER_ADDRESS = "0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"

# --- SIMULATED INFRASTRUCTURE ---
class EthereumMainnet:
    def __init__(self):
        self.balances = {USER_ADDRESS: 10.0}
        self.bridge_vault = 0.0
        print("🌐 [ETH] Mainnet Initialized.")

    def deposit_to_bridge(self, user, amount):
        if self.balances.get(user, 0) >= amount:
            self.balances[user] -= amount
            self.bridge_vault += amount
            return True
        return False

    def release_from_bridge(self, user, amount):
        if self.bridge_vault >= amount:
            self.bridge_vault -= amount
            self.balances[user] = self.balances.get(user, 0) + amount
            return True
        return False

class TrojanChain:
    def __init__(self):
        self.balances = {}
        print("🛡️ [Trojan] Chain Initialized.")

    def mint_t_eth(self, user, amount):
        self.balances[user] = self.balances.get(user, 0) + amount

    def burn_t_eth(self, user, amount):
        if self.balances.get(user, 0) >= amount:
            self.balances[user] -= amount
            return True
        return False

class TrojanBridgeRelayer:
    def __init__(self, eth_chain, trojan_chain):
        self.eth = eth_chain
        self.trojan = trojan_chain

    def bridge_eth_to_trojan(self, user, amount):
        if self.eth.deposit_to_bridge(user, amount):
            self.trojan.mint_t_eth(user, amount)
            return True
        return False

    def bridge_trojan_to_eth(self, user, amount):
        if self.trojan.burn_t_eth(user, amount):
            if self.eth.release_from_bridge(user, amount):
                return True
            else:
                self.trojan.mint_t_eth(user, amount) 
                print("[Relayer] ⚠️ Bridge Vault empty, refunding T-ETH to user.")
        return False

# --- TEST SUITE ---
def run_withdrawal_tests():
    eth = EthereumMainnet()
    trojan = TrojanChain()
    relayer = TrojanBridgeRelayer(eth, trojan)

    print("\n" + "="*50)
    print("🧪 TROJAN BRIDGE: WITHDRAWAL TEST SUITE")
    print("="*50)

    # SETUP: Deposit 5 ETH to start
    relayer.bridge_eth_to_trojan(USER_ADDRESS, 5.0)
    print(f"Setup: User has 5.0 T-ETH and 5.0 ETH on Mainnet.")

    # TEST 1: Successful Withdrawal
    print("\nTest 1: Valid Withdrawal (2.0 T-ETH) ...")
    if relayer.bridge_trojan_to_eth(USER_ADDRESS, 2.0):
        print("✅ SUCCESS: 2.0 T-ETH withdrawn and converted to ETH.")
    else:
        print("❌ FAILED: Valid withdrawal rejected.")

    # TEST 2: Insufficient T-ETH (Over-withdraw)
    print("\nTest 2: Over-Withdraw (10.0 T-ETH) ...")
    if relayer.bridge_trojan_to_eth(USER_ADDRESS, 10.0):
        print("❌ FAILED: User withdrew more than they owned!")
    else:
        print("✅ SUCCESS: System blocked over-withdrawal.")

    # TEST 3: Unauthorized Wallet (Empty Wallet)
    print("\nTest 3: Withdrawal from Empty Wallet ...")
    if relayer.bridge_trojan_to_eth(ATTACKER_ADDRESS, 1.0):
        print("❌ FAILED: Attacker managed to withdraw funds!")
    else:
        print("✅ SUCCESS: System blocked unauthorized withdrawal.")

    print("\n" + "="*50)
    print("FINAL BALANCES")
    print(f"User ETH Balance: {eth.balances[USER_ADDRESS]} ETH")
    print(f"User T-ETH Balance: {trojan.balances.get(USER_ADDRESS, 0)} T-ETH")
    print(f"Bridge Vault Balance: {eth.bridge_vault} ETH")
    print("="*50)

if __name__ == "__main__":
    run_withdrawal_tests()
