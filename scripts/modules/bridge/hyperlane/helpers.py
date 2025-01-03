HYPERLANE_MIN_TRANSACTION_AMOUNT = 0.00001
HYPERLANE_MAX_TRANSACTION_AMOUNTS = {
    "optimism": 0.5,
    "arbitrum": 0.5,
    "base": 0.5,
    "scroll": 1,
    "linea": 1,
}
HYPERLANE_CONTRACTS = {
    "optimism": "0xC110E7FAA95680c79937CCACa3d1caB7902bE25e",
    "arbitrum": "0x233888F5Dc1d3C0360b559aBc029675290DAFa70",
    "base": "0x0cb0354E9C51960a7875724343dfC37B93d32609",
    "scroll": "0xc0faBF14f8ad908b2dCE4C8aA2e7c1a6bD069957",
    "linea": "0x8F2161c83F46B46628cb591358dE4a89A63eEABf",
}

HYPERLANE_ABI = [
    {
        "type": "function",
        "name": "quoteBridge",
        "constant": True,
        "stateMutability": "view",
        "payable": False,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"},
        ],
        "outputs": [{"type": "uint256", "name": "fee"}],
    },
    {
        "type": "function",
        "name": "bridgeETH",
        "constant": False,
        "stateMutability": "payable",
        "payable": True,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"},
        ],
        "outputs": [{"type": "bytes32", "name": "messageId"}],
    },
    {
        "type": "function",
        "name": "bridgeWETH",
        "constant": False,
        "stateMutability": "payable",
        "payable": True,
        "inputs": [
            {"type": "uint32", "name": "_destination"},
            {"type": "uint256", "name": "amount"},
        ],
        "outputs": [{"type": "bytes32", "name": "messageId"}],
    },
]
