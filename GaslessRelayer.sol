// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title GaslessRelayer
 * @dev This contract allows users to transfer ETH or Tokens via signed messages.
 * The Relayer pays the gas, and the contract verifies the signature.
 */
contract GaslessRelayer {
    mapping(address => uint256) public nonces;

    event TransferExecuted(address indexed from, address indexed to, uint256 amount);

    // EIP-712 Domain Separator
    bytes32 public DOMAIN_SEPARATOR;

    constructor() {
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("GaslessTransferApp"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }

    /**
     * @dev Executes a transfer based on a signed message.
     * @param from The address of the sender.
     * @param to The address of the recipient.
     * @param amount The amount of ETH to transfer.
     * @param nonce The nonce to prevent replay attacks.
     * @param signature The EIP-712 signature.
     */
    function executeTransfer(
        address from,
        address to,
        uint256 amount,
        uint256 nonce,
        bytes memory signature
    ) public {
        require(nonce == nonces[from], "Invalid nonce");

        // Recreate the EIP-712 hash
        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Transfer(address from,address to,uint256 amount,uint256 nonce)"),
                from,
                to,
                amount,
                nonce
            )
        );

        bytes32 hash = keccak256(
            abi.encodePacked(DOMAIN_SEPARATOR, structHash)
        );

        // Recover the signer from the signature
        address signer = recoverSigner(hash, signature);
        require(signer == from, "Invalid signature");

        // Increment nonce to prevent replay
        nonces[from]++;

        // Transfer the ETH
        // NOTE: This requires the 'from' address to have given this contract 
        // permission or for the contract to hold the funds. 
        // For a direct ETH transfer from a user's wallet, the user must use 
        // a 'permit' or 'approve' logic for tokens.
        // For simplicity in this logic, we assume the contract is used 
        // as a vault or the user has deposited funds.
        
        payable(to).transfer(amount);

        emit TransferExecuted(from, to, amount);
    }

    function recoverSigner(bytes32 hash, bytes memory signature) internal pure returns (address) {
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
        return ecrecover(hash, v, r, s);
    }

    function splitSignature(bytes memory sig) internal pure returns (bytes32 r, bytes32 s, uint8 v) {
        require(sig.length == 65, "Invalid signature length");
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
    }
}
