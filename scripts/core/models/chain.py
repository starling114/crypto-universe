import random

from utils import ExecutionError


class Chain:
    def __init__(self, name, chain_id, native_symbol, tokens, scan, rpcs, private_rpcs):
        self.name = name
        self.chain_id = chain_id
        self.native_symbol = native_symbol
        self.tokens = tokens
        self.scan = scan
        self.rpcs = rpcs
        self.private_rpcs = private_rpcs

    def random_rpc(self, private=False):
        if private:
            if len(self.private_rpcs) == 0:
                raise ExecutionError("No private RPCs available for this chain")

            return random.choice(self.private_rpcs)
        else:
            if len(self.rpcs) == 0:
                raise ExecutionError("No RPCs available for this chain")

            return random.choice(self.rpcs)
