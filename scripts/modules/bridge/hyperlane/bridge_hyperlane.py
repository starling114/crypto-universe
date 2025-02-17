from core.helpers import transaction_data
from modules.bridge.bridge_base import BridgeBase
from modules.bridge.hyperlane.helpers import (
    HYPERLANE_CONTRACTS,
    HYPERLANE_ABI,
    HYPERLANE_MIN_TRANSACTION_AMOUNT,
    HYPERLANE_MAX_TRANSACTION_AMOUNTS,
    HYPERLANE_MAX_DEFAULT_TRANSACTION_AMOUNT,
)


class BridgeHyperlane(BridgeBase):
    def __init__(
        self,
        secrets,
        leave_balance,
        leave_balance_amount,
        amount,
        address,
        from_chain,
        to_chain,
        from_token,
        to_token,
        amount_includes_fee,
        web3,
    ):
        super().__init__(
            secrets,
            leave_balance,
            leave_balance_amount,
            amount,
            address,
            from_chain,
            to_chain,
            from_token,
            to_token,
            amount_includes_fee,
            web3,
        )
        self.bridge_contract = self.web3.eth.contract(
            address=HYPERLANE_CONTRACTS[self.from_chain.name], abi=HYPERLANE_ABI
        )

    def calculate_fee(self, base_amount):
        bridge_fee_tmp = self.bridge_contract.functions.quoteBridge(self.to_chain.chain_id, base_amount).call()
        bridge_fee = self.bridge_contract.functions.quoteBridge(
            self.to_chain.chain_id, base_amount - bridge_fee_tmp
        ).call()
        return bridge_fee

    def min_transaction_amount(self):
        return HYPERLANE_MIN_TRANSACTION_AMOUNT

    def max_transaction_amount(self):
        return HYPERLANE_MAX_TRANSACTION_AMOUNTS.get(self.from_chain.name, HYPERLANE_MAX_DEFAULT_TRANSACTION_AMOUNT)

    def get_transaction_data(self):
        fee = self.bridge_contract.functions.quoteBridge(self.to_chain.chain_id, self.calculated_amount).call()

        tx_pre_data = transaction_data(self.web3, from_address=self.address, value=self.calculated_amount + fee)
        tx_data = self.bridge_contract.functions.bridgeETH(
            self.to_chain.chain_id, self.calculated_amount
        ).build_transaction(tx_pre_data)

        return tx_data

    @classmethod
    def run(cls):
        super().run("hyperlane")
