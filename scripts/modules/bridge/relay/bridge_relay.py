from modules.bridge.bridge_base import BridgeBase

from utils import (
    post_call,
    get_balance,
    get_transactions_count,
    get_gas_price,
    get_gas_limit,
)

RELAY_MIN_TRANSACTION_AMOUNT = 0.00005
NULL_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"


class BridgeRelay(BridgeBase):
    def get_data(self):
        # TODO: Change NULL_TOKEN_ADDRESS to symbol address to support other tokens
        params = {
            "user": self.address,
            "recipient": self.address,
            "originChainId": self.configs["chains"][self.from_chain]["chain_id"],
            "destinationChainId": self.configs["chains"][self.to_chain]["chain_id"],
            "originCurrency": NULL_TOKEN_ADDRESS,
            "destinationCurrency": NULL_TOKEN_ADDRESS,
            "amount": str(self.calculated_amount),
            "tradeType": "EXACT_INPUT",
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
        }

        return post_call("https://api.relay.link/quote", json=params)

    def calculate_amount(self):
        amount = 0
        balance = get_balance(self.web3, self.address)
        amount = self.calculate_amount_base(balance)

        self.amount_validations(balance, amount, RELAY_MIN_TRANSACTION_AMOUNT)

        self.calculated_amount = amount

    def get_contract_txn(self):
        self.calculate_amount()

        tx_data = self.get_data()
        transaction_data = tx_data["steps"][0]["items"][0]["data"]

        contract_txn = {
            "from": self.web3.to_checksum_address(transaction_data["from"]),
            "nonce": get_transactions_count(self.web3, self.address),
            "value": int(transaction_data["value"]),
            "to": self.web3.to_checksum_address(transaction_data["to"]),
            "data": transaction_data["data"],
            "chainId": transaction_data["chainId"],
            "gas": 0,
            "gasPrice": 0,
        }
        contract_txn["gas"] = get_gas_limit(self.web3, contract_txn)
        contract_txn["gasPrice"] = get_gas_price(self.web3)

        return contract_txn

    @classmethod
    def run(cls):
        super().run("relay")
