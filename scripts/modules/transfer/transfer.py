import random

from utils import load_json, log_error, wei_to_int, debug_mode, sleep, logger
from core.helpers import (
    calculate_token_balance,
    calculate_base_amount,
    transaction_data,
    send_transaction,
    verify_transaction,
    estimate_fee,
    execute_amount_validations,
    get_private_key,
    get_transaction_link,
    zip_to_objects,
    prettify_seconds,
    prettify_number,
)
from core.models.helpers import build_token, build_chain, build_web3


class Transfer:
    def __init__(
        self,
        secrets,
        leave_balance,
        leave_balance_amount,
        source_address,
        amount,
        destinaion_address,
        chain,
        token,
        web3,
    ):
        self.secrets = secrets
        self.leave_balance = leave_balance
        self.leave_balance_amount = leave_balance_amount
        self.source_address = source_address
        self.amount = amount
        self.destinaion_address = destinaion_address
        self.chain = chain
        self.token = token
        self.web3 = web3

    def calculate_fee(self, base_amount):
        tx_data = self.get_transaction_data(base_amount)

        return estimate_fee(self.web3, tx_data)

    def calculate_amount(self):
        balance = calculate_token_balance(self.web3, self.source_address, self.token)
        amount = calculate_base_amount(balance, self.amount, self.leave_balance, self.leave_balance_amount)

        if self.token.is_native() and self.leave_balance and float(self.leave_balance_amount) == 0:
            fee = self.calculate_fee(amount)
            amount = amount - fee

        execute_amount_validations(balance, amount)

        return amount

    def get_transaction_data(self, amount):
        if self.token.is_native():
            return transaction_data(
                self.web3,
                from_address=self.source_address,
                to_address=self.destinaion_address,
                value=amount,
            )
        else:
            tx_pre_data = transaction_data(self.web3, from_address=self.source_address)
            tx_data = self.token.contract.functions.transfer(
                self.web3.to_checksum_address(self.destinaion_address),
                amount,
            ).build_transaction(tx_pre_data)

            return tx_data

    def transfer(self):
        try:
            calculated_amount = self.calculate_amount()
            private_key = get_private_key(self.web3, self.source_address, self.secrets)
            tx_data = self.get_transaction_data(calculated_amount)

            if debug_mode():
                logger.info(f"{get_transaction_link(self.chain, 'DEBUG')}")
                logger.success(
                    f"{self.source_address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Transfer successful"
                )
                return True

            tx_hash = send_transaction(self.web3, tx_data, private_key, fees_v2=True)

            logger.info(f"{get_transaction_link(self.chain, tx_hash)}")

            if verify_transaction(self.web3, tx_hash):
                logger.success(
                    f"{self.source_address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Transfer successful"
                )
                return True
            else:
                logger.error(
                    f"{self.source_address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Transfer unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.source_address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/transfer/instructions.json")
        secrets = load_json("modules/transfer/secrets.json")

        source_addresses = instructions["source_addresses"]
        amounts = zip_to_objects(source_addresses, instructions["amounts"])
        destinaion_addresses = zip_to_objects(source_addresses, instructions["destinaion_addresses"])

        if instructions["randomize"]:
            random.shuffle(source_addresses)

        chain = build_chain(instructions["chain"])
        web3 = build_web3(chain)

        if instructions["use_custom_symbol"]:
            token = build_token(web3, token_address=instructions["custom_symbol"])
        else:
            token = build_token(web3, chain=chain, symbol=instructions["symbol"])

        last_address = len(source_addresses) - 1
        for index, source_address in enumerate(source_addresses):
            amount = None if instructions["leave_balance"] else amounts[source_address]
            result = cls(
                secrets,
                instructions["leave_balance"],
                instructions["leave_balance_amount"],
                source_address,
                amount,
                destinaion_addresses[source_address],
                chain,
                token,
                web3,
            ).transfer()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {prettify_seconds(sleep_time)}")
                sleep(sleep_time)
