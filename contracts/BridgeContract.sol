// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrojanBridge
 * @dev Handles the locking and unlocking of ETH for the Trojan Chain Bridge.
 */
contract TrojanBridge {
    address public relayer;
    mapping(address => uint256) public lockedBalances;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    constructor() {
        relayer = msg.sender; // The person deploying is the initial relayer
    }

    modifier onlyRelayer() {
        require(msg.sender == relayer, "Only relayer can call this");
        _;
    }

    // User deposits ETH into the bridge to get T-ETH on Trojan Chain
    function deposit() public payable {
        require(msg.value > 0, "Amount must be greater than 0");
        lockedBalances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    // Relayer calls this to release ETH when user burns T-ETH on Trojan Chain
    function release(address user, uint256 amount) public onlyRelayer {
        require(lockedBalances[user] >= amount, "Insufficient locked balance");
        
        lockedBalances[user] -= amount;
        payable(user).transfer(amount);
        
        emit Withdrawn(user, amount);
    }

    function setRelayer(address _newRelayer) public onlyRelayer {
        relayer = _newRelayer;
    }
}
