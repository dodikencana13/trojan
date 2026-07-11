from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia.publicnode.com'))
balance = w3.eth.get_balance('0x8A339E44b2aceaa1F57bdD5ecd040fF0a18930eB')
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
