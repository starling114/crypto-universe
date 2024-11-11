from modules.withdraw.withdraw_base import WithdrawBase

from utils import logger, humanify_number, debug_mode

OKX_CHAIN_MAPPING = {
    "ethereum": "ERC20",
    "arbitrum": "Arbitrum One",
    "base": "Base",
    "optimism": "Optimism",
}


class WithdrawOkx(WithdrawBase):
    def __init__(
        self, cex, secrets, address, chain, symbol, amount_includes_fee, amount
    ):
        super().__init__(
            cex,
            secrets,
            address,
            OKX_CHAIN_MAPPING[chain],
            symbol,
            amount_includes_fee,
            amount,
        )

    def params(self):
        params = super().params()

        self.exchange.load_markets()
        networks = self.exchange.currencies[self.symbol]["networks"]

        params["fee"] = networks[self.network]["fee"]
        params["pwd"] = self.secrets["password"]

        return params

    @classmethod
    def run(cls):
        super().run("okx")
