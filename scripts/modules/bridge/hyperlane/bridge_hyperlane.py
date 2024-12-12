from modules.bridge.bridge_base import BridgeBase
from modules.bridge.hyperlane.helpers import *

from utils import (
    get_balance,
    get_transactions_count,
    get_gas_price,
    get_gas_limit,
)

HYPERLANE_MIN_TRANSACTION_AMOUNT = 0.00001
HYPERLANE_MAX_TRANSACTION_AMOUNT = 0.5


class BridgeHyperlane(BridgeBase):
    def calculate_amount(self, bridge_contract, to_chain_id):
        amount = 0
        balance = get_balance(self.web3, self.address)
        amount = self.calculate_amount_base(balance)

        bridge_fee_tmp = bridge_contract.functions.quoteBridge(to_chain_id, amount).call()
        bridge_fee = bridge_contract.functions.quoteBridge(to_chain_id, amount - bridge_fee_tmp).call()
        amount = amount - bridge_fee

        self.amount_validations(
            balance,
            amount,
            HYPERLANE_MIN_TRANSACTION_AMOUNT,
            HYPERLANE_MAX_TRANSACTION_AMOUNT,
        )

        self.calculated_amount = amount

    def get_contract_txn(self):
        bridge_contract = self.web3.eth.contract(address=HYPERLANE_CONTRACTS[self.from_chain], abi=HYPERLANE_ABI)
        to_chain_id = self.configs["chains"][self.to_chain]["chain_id"]

        self.calculate_amount(bridge_contract, to_chain_id)

        amount_without_fee = self.calculated_amount
        fee = bridge_contract.functions.quoteBridge(to_chain_id, amount_without_fee).call()
        self.calculated_amount = amount_without_fee + fee

        contract_txn = bridge_contract.functions.bridgeETH(to_chain_id, amount_without_fee).build_transaction(
            {
                "nonce": get_transactions_count(self.web3, self.address),
                "from": self.web3.to_checksum_address(self.address),
                "value": self.calculated_amount,
                "gas": 0,
                "gasPrice": 0,
            }
        )
        contract_txn["gas"] = get_gas_limit(self.web3, contract_txn)
        contract_txn["gasPrice"] = get_gas_price(self.web3)

        return contract_txn

    @classmethod
    def run(cls):
        super().run("hyperlane")
