from eth_account import Account

def generate_attacker():
    acc = Account.create()
    print(f"ATTACKER_ADDRESS: {acc.address}")
    print(f"ATTACKER_PRIVATE_KEY: {acc.key.hex()}")

if __name__ == "__main__":
    generate_attacker()
