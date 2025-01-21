from modules.withdraw.withdraw_base import WithdrawBase
from modules.withdraw.okx.helpers import OKX_CHAINS_MAPPING


class WithdrawOkx(WithdrawBase):
    def calculate_fee(self):
        return self.withdraw_params()["fee"]

    def cex_details(self):
        details = super().cex_details()
        details["password"] = self.secrets["password"]

        return details

    def withdraw_params(self):
        if self._withdraw_params is None:
            self.exchange.load_markets()
            network = OKX_CHAINS_MAPPING[self.chain]

            self._withdraw_params = {
                "network": network,
                "fee": self.exchange.currencies[self.symbol]["networks"][network]["fee"],
                "pwd": self.secrets["password"],
            }

        return self._withdraw_params

    @classmethod
    def run(cls):
        super().run("okx")
