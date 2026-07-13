// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrojanPaymaster
 * @dev The "Gas Tank" for the Trojan Chain. 
 * This contract sponsors the gas for users who don't have ETH.
 */
contract TrojanPaymaster {
    address public admin;
    mapping(address => bool) public sponsoredUsers;
    uint256 public totalSponsorships;

    event GasSponsored(address indexed user, uint256 gasPaid);

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    // Admin adds a user to the sponsored list
    function addSponsoredUser(address user) external onlyAdmin {
        sponsoredUsers[user] = true;
    }

    // This function is called by the EntryPoint to verify if the Paymaster will pay
    function validatePaymasterUserOp(
        address userOpSender, 
        bytes calldata userOpHash, 
        uint256 maxCost
    ) external returns (bytes memory context, uint256 validationData) {
        require(sponsoredUsers[userOpSender], "User is not sponsored by Trojan Paymaster");
        
        totalSponsorships++;
        emit GasSponsored(userOpSender, maxCost);
        
        return ("", 0);
    }

    // Function to top up the Paymaster's gas tank
    receive() external payable {}
}
