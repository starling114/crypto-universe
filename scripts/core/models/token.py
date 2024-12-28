class Token:
    def __init__(self, symbol, address, contract, decimals):
        self.symbol = symbol
        self.address = address
        self.contract = contract
        self.decimals = decimals

    def is_native(self):
        return self.contract is None
