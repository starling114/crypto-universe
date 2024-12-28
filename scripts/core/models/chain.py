import random


class Chain:
    def __init__(self, name, chain_id, native_symbol, tokens, scan, rpcs):
        self.name = name
        self.chain_id = chain_id
        self.native_symbol = native_symbol
        self.tokens = tokens
        self.scan = scan
        self.rpcs = rpcs

    def random_rpc(self):
        return random.choice(self.rpcs)
