// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrojanAccount
 * @dev A Smart Contract Wallet for the Trojan Chain.
 * This account allows for gasless transactions via Account Abstraction.
 */
contract TrojanAccount {
    address public owner;

    event Deposit(address indexed sender, uint256 amount);
    event Execution(address indexed target, uint256 value, bytes data);

    constructor() {
        owner = msg.sender;
    }

    // This function is called by the EntryPoint contract
    function execute(address target, uint256 value, bytes calldata data) external {
        // In a real AA setup, the EntryPoint verifies the signature first
        (bool success, ) = target.call{value: value}(data);
        require(success, "Execution failed");
        emit Execution(target, value, data);
    }

    function transferOwnership(address newOwner) external {
        require(msg.sender == owner, "Only owner can transfer");
        owner = newOwner;
    }

    receive() external payable {
        emit Deposit(msg.sender, msg.value);
    }
}
