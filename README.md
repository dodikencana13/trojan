# 🛡️ Trojan Chain (T-ETH)
### The Future of Gasless Blockchain Infrastructure

Welcome to the official repository of the **Trojan Chain**, a high-performance Layer 1 blockchain engineered to eliminate the "Gas Wall" and enable mass adoption of decentralized applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ChainID: 1303](https://img.shields.io/badge/ChainID-1303-blue)](https://etherscan.io)

---

## 🌟 Vision
Trojan Chain is designed on the premise that **blockchain should be invisible**. By decoupling the transaction authorization from the payment layer, we allow users to interact with the blockchain without ever needing to hold a native token for gas.

## 🚀 Core Innovations
- **Gasless Relayer Architecture**: A specialized node system that sponsors user transactions.
- **Sovereign Identity**: Full integration of EIP-712 structured data for secure, off-chain intents.
- **Hyper-Efficient State**: A custom-built state-transition engine optimized for low latency.
- **EVM Compatibility**: Build, deploy, and migrate your Ethereum apps with zero code changes.

## 📁 Project Structure
- `/docs`: Full technical and economic specifications.
- `/src`: Core RPC server and blockchain engine.
- `/contracts`: Solidity smart contracts for the Relayer and Ecosystem.

## 📖 Documentation
For a deep dive into the Trojan Chain, please visit our documentation:
- [📖 Whitepaper](./docs/WHITEPAPER.md) - The vision and technical philosophy.
- [💰 Tokenomics](./docs/TOKENOMICS.md) - The T-ETH economic model.
- [🛠️ Developer Guide](./docs/DOCUMENTATION.md) - How to build on Trojan Chain.
- [🏗️ Architecture](./docs/ARCHITECTURE.md) - Deep dive into the la-relay system.

## 🛠️ Quick Launch
To run your own Trojan Node locally:
```bash
pip install -r requirements.txt
python src/trojan_rpc_sqlite.py
```

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
