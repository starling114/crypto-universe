import random

from utils import load_json, wei_to_int, log_error, debug_mode, sleep, logger
from core.helpers import (
    calculate_token_balance,
    calculate_base_amount,
    send_transaction,
    verify_transaction,
    execute_amount_validations,
    get_private_key,
    get_transaction_link,
    zip_to_addresses,
    prettify_seconds,
    prettify_number,
)
from core.models.helpers import build_token, build_chain, build_web3


class BridgeBase:
    MIN_TRANSACTION_AMOUNT = 0.0000001
    MAX_TRANSACTION_AMOUNT = 1000

    def __init__(
        self,
        secrets,
        leave_balance,
        leave_balance_amount,
        amount,
        address,
        from_chain,
        to_chain,
        web3,
        token,
        amount_includes_fee,
    ):
        self.secrets = secrets
        self.leave_balance = leave_balance
        self.leave_balance_amount = leave_balance_amount
        self.amount = amount
        self.address = address
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.web3 = web3
        self.token = token
        self.amount_includes_fee = amount_includes_fee

    def calculate_fee(self, _):
        raise NotImplementedError

    def min_transaction_amount(self):
        return self.MIN_TRANSACTION_AMOUNT

    def max_transaction_amount(self):
        return self.MAX_TRANSACTION_AMOUNT

    def calculate_amount(self):
        balance = calculate_token_balance(self.web3, self.address, self.token)
        amount = calculate_base_amount(balance, self.amount, self.leave_balance, self.leave_balance_amount)

        if self.amount_includes_fee and self.token.is_native():
            amount = amount - self.calculate_fee(amount)

        execute_amount_validations(balance, amount, self.min_transaction_amount(), self.max_transaction_amount())

        return amount

    def get_transaction_data(self):
        raise NotImplementedError

    def bridge(self):
        try:
            self.calculated_amount = self.calculate_amount()

            if debug_mode():
                logger.info(f"{get_transaction_link(self.from_chain, 'DEBUG')}")
                logger.success(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(self.calculated_amount))} | Bridge successful"
                )
                return True

            self.private_key = get_private_key(self.web3, self.secrets, self.address)
            tx_data = self.get_transaction_data()
            tx_hash = send_transaction(self.web3, tx_data, self.private_key)

            logger.info(f"{get_transaction_link(self.from_chain, tx_hash)}")

            if verify_transaction(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(self.calculated_amount))} | Bridge successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(self.calculated_amount))} | Bridge unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls, bridge):
        instructions = load_json(f"modules/bridge/{bridge}/instructions.json")
        secrets = load_json(f"modules/bridge/{bridge}/secrets.json")

        addresses = instructions["addresses"]
        amounts = zip_to_addresses(addresses, instructions["amounts"])

        if instructions["randomize"]:
            random.shuffle(addresses)

        from_chain = build_chain(instructions["from_chain"])
        to_chain = build_chain(instructions["to_chain"])
        web3 = build_web3(from_chain)
        token = build_token(web3, chain=from_chain, symbol=instructions["symbol"])

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            amount = None if instructions["leave_balance"] else amounts[address]
            result = cls(
                secrets,
                instructions["leave_balance"],
                instructions["leave_balance_amount"],
                amount,
                address,
                from_chain,
                to_chain,
                web3,
                token,
                instructions["amount_includes_fee"],
            ).bridge()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {prettify_seconds(sleep_time)}")
                sleep(sleep_time)
