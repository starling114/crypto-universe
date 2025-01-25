HYPERLANE_MIN_TRANSACTION_AMOUNT = 0.00001
HYPERLANE_MAX_DEFAULT_TRANSACTION_AMOUNT = 0.5
HYPERLANE_MAX_TRANSACTION_AMOUNTS = {
    "scroll": 1,
    "linea": 1,
    "taiko": 1,
}
HYPERLANE_CONTRACTS = {
    "optimism": "0xC110E7FAA95680c79937CCACa3d1caB7902bE25e",
    "arbitrum": "0x233888F5Dc1d3C0360b559aBc029675290DAFa70",
    "base": "0x0cb0354E9C51960a7875724343dfC37B93d32609",
    "scroll": "0xc0faBF14f8ad908b2dCE4C8aA2e7c1a6bD069957",
    "linea": "0x8F2161c83F46B46628cb591358dE4a89A63eEABf",
    "mode": "0x9970cB23f10dBd95B8A3E643f3A6A6ABB6f3cB9b",
    # "zora": "0x8028d4f11d10730B12Ae011474F9db8140F112F4",  # TODO: Check this address
    # "taiko": "0xb08ab8cBd0226D8335fB0Cb88ce47FAfC9C47096",  # TODO: Check this address
    # "zircuit": "0xA5f471A19fdB367Ea80c4c82ecd30eA94090d549",  # TODO: Check this address
    # mantapacific
    # morph
    # https://github.com/hyperlane-xyz/hyperlane-monorepo/blob/db8c09011274905ccbfe56c6b3d6c2d5d98d8f2a/typescript/infra/config/environments/mainnet3/misc-artifacts/merkly-eth-addresses.json#L39
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
