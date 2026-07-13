# 📘 Trojan Chain Technical Documentation

Welcome to the official developer guide for Trojan Chain.

## 🌐 Network Configuration
To connect your wallet to the Trojan Chain, use the following settings:

- **Network Name**: Trojan Chain
- **RPC URL**: `https://your-rpc-url.com`
- **Chain ID**: `1303`
- **Currency Symbol**: `T-ETH`
- **Block Explorer**: `https://explorer.trojanchain.io`

## 🛠️ For Developers

### Implementing Gasless Transfers
To enable gasless transfers in your DApp, follow the EIP-712 flow:

1. **Define the Transfer Type**:
   Create a structured data object containing `from`, `to`, `amount`, and `nonce`.
2. **User Signature**:
   Request the user to sign the data using `eth_signTypedData_v4`.
3. **Submit to Relayer**:
   Send the signature to the Trojan Relayer RPC endpoint.

### RPC API Reference
| Method | Parameters | Description |
| :--- | :--- | :--- |
| `eth_getBalance` | `[address]` | Returns the T-ETH balance. |
| `eth_blockNumber` | `[]` | Returns the latest block height. |
| `eth_chainId` | `[]` | Returns the chain ID (1303). |

## 🛡️ Security
Trojan Chain uses a **Nonce-Verification System**. Every gasless signature must include a strictly increasing nonce to prevent "Replay Attacks" (where a transaction is submitted multiple times).
