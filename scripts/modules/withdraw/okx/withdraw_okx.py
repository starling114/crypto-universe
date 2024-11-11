from modules.withdraw.withdraw_base import WithdrawBase

from utils import logger, humanify_number

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

    def withdraw(self):
        params = self.params()
        calculated_amount = self.calculate_amount(params["fee"])

        logger.success(
            f"{self.address} | {self.symbol} | {humanify_number(calculated_amount)} | Withdrawal successful"
        )
        return True

    @classmethod
    def run(cls):
        super().run("okx")
