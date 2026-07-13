# 🏗️ Trojan Chain Architecture Deep-Dive

Trojan Chain is engineered to solve the "UX Gap" of existing blockchains. Below is the technical breakdown of the system architecture.

## 1. The Layered Model
Trojan Chain operates on a three-layer stack:
- **Execution Layer**: A modified EVM-compatible engine that processes state changes.
- **Sponsorship Layer**: The "Paymaster" interface where Relayers manage the gas budget for users.
- **Settlement Layer**: The final ledger where transactions are permanently recorded.

## 2. The Gasless Flow (Step-by-Step)
Unlike standard Ethereum transactions, Trojan Chain uses an **Asynchronous Payment Model**:

1. **Client-Side**: User signs an `Intent` $\rightarrow$ `Signature`.
2. **Transmission**: `Signature` $\rightarrow$ `Trojan Relayer`.
3. **Verification**: Relayer $\rightarrow$ `Contract.verify(Signature)`.
4. **Payment**: Relayer $\rightarrow$ `Network.payGas()`.
5. **Commit**: `Network` $\rightarrow$ `Update State`.

## 3. State Management
The chain utilizes a **Key-Value State Store** for balances and nonces, optimized for high-frequency read/write operations. By utilizing a customized RPC server, Trojan Chain reduces the overhead of traditional JSON-RPC, allowing for faster block production.

## 4. Security Analysis
- **Replay Protection**: Nonces are tracked per address.
- **Signature Integrity**: EIP-712 ensures that users know exactly what they are signing (Amount, Destination, Chain ID).
- **Relayer Trust**: Relayers are incentivized via T-ETH staking, ensuring they only process valid, authorized signatures.
