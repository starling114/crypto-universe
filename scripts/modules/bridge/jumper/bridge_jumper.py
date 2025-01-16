from utils import post_call, ExecutionError
from core.helpers import transaction_data, approve_token, estimate_gas
from modules.bridge.bridge_base import BridgeBase
from modules.bridge.jumper.helpers import MAX_SLIPPAGE


class BridgeJumper(BridgeBase):

    def get_remote_data(self, amount):
        headers = {"X-Lifi-Sdk": "3.0.0-alpha.57", "X-Lifi-Widget": "3.0.0-alpha.35"}
        params = {
            "fromAddress": self.address,
            "fromAmount": str(amount),
            "fromChainId": self.from_chain.chain_id,
            "fromTokenAddress": self.token.address,
            "toAddress": self.address,
            "toChainId": self.to_chain.chain_id,
            "toTokenAddress": self.token.address,
            "options": {
                "integrator": "jumper.exchange",
                "order": "CHEAPEST",
                "slippage": MAX_SLIPPAGE / 100,
                "maxPriceImpact": 1,
                "allowSwitchChain": False,
                "insurance": False,
            },
        }
        route_data = post_call("https://li.quest/v1/advanced/routes", headers=headers, json=params)

        if len(route_data["routes"]) <= 0:
            raise ExecutionError("No swap routes found")

        data = post_call(
            "https://li.quest/v1/advanced/stepTransaction", headers=headers, json=route_data["routes"][0]["steps"][0]
        )

        return data["transactionRequest"]

    def calculate_fee(self, base_amount):
        remote_data = self.get_remote_data(base_amount)
        value = int(remote_data["value"], 16)
        tx_data = transaction_data(
            self.web3, from_address=self.address, to_address=remote_data["to"], data=remote_data["data"], value=value
        )
        gas_fee = estimate_gas(self.web3, tx_data) * tx_data["gasPrice"]
        jumper_fee = value - base_amount
        return gas_fee + jumper_fee

    def get_transaction_data(self):
        remote_data = self.get_remote_data(self.calculated_amount)
        remote_value = int(remote_data["value"], 16)

        approve_token(self.web3, self.token, self.calculated_amount, remote_data["to"], self.address, self.private_key)

        return transaction_data(
            self.web3,
            from_address=self.address,
            to_address=remote_data["to"],
            data=remote_data["data"],
            value=remote_value,
        )

    @classmethod
    def run(cls):
        super().run("jumper")
