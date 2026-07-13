from web3 import Web3

RPC_URL = "https://ethereum-rpc.publicnode.com"
ADDRESS = "0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB"

def check_mainnet_balance():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    try:
        balance_wei = w3.eth.get_balance(ADDRESS)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        print(f"Mainnet ETH Balance for {ADDRESS}: {balance_eth} ETH")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mainnet_balance()
