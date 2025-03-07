from utils import post_call
from core.helpers import transaction_data
from modules.bridge.bridge_base import BridgeBase
from modules.bridge.relay.helpers import RELAY_MIN_TRANSACTION_AMOUNT


class BridgeRelay(BridgeBase):

    def get_remote_data(self, amount):
        params = {
            "user": self.address,
            "recipient": self.address,
            "originChainId": self.from_chain.chain_id,
            "destinationChainId": self.to_chain.chain_id,
            "originCurrency": self.from_token.address,
            "destinationCurrency": self.to_token.address,
            "amount": str(amount),
            "tradeType": "EXACT_INPUT",
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
        }

        return post_call("https://api.relay.link/quote", json=params)

    def min_transaction_amount(self):
        return RELAY_MIN_TRANSACTION_AMOUNT

    def get_transaction_data(self):
        remote_data = self.get_remote_data(self.calculated_amount)["steps"][0]["items"][0]["data"]

        return transaction_data(
            self.web3,
            from_address=remote_data["from"],
            to_address=remote_data["to"],
            data=remote_data["data"],
            value=int(remote_data["value"]),
        )

    @classmethod
    def run(cls):
        super().run("relay")
