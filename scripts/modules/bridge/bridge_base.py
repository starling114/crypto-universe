from web3 import Web3
import random

from utils import (
    NULL_TOKEN_ADDRESS,
    load_json,
    int_to_wei,
    wei_to_int,
    sign_tx,
    zip_to_addresses,
    humanify_seconds,
    humanify_number,
    get_private_key,
    get_tx_link,
    wait_tx_completion,
    log_error,
    debug_mode,
    sleep,
    ExecutionError,
)
from utils import logger

MIN_TRANSACTION_AMOUNT = 0.00001
MAX_TRANSACTION_AMOUNT = 9999999


class BridgeBase:
    def __init__(
        self,
        secrets,
        configs,
        leave_balance,
        leave_balance_amount,
        amount,
        address,
        from_chain,
        to_chain,
        symbol,
        web3,
    ):
        self.secrets = secrets
        self.configs = configs
        self.leave_balance = leave_balance
        self.leave_balance_amount = leave_balance_amount
        self.amount = amount
        self.calculated_amount = None
        self.address = address
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.symbol = symbol
        self.web3 = web3

    def amount_validations(
        self,
        balance,
        amount,
        min_transaction_amount=MIN_TRANSACTION_AMOUNT,
        max_transaction_amount=MAX_TRANSACTION_AMOUNT,
    ):
        min_amount = int_to_wei(min_transaction_amount)
        max_amount = int_to_wei(max_transaction_amount)
        if amount > balance:
            raise ExecutionError(
                f"Not enough balance. Amount > Balance ({humanify_number(wei_to_int(amount))} > {humanify_number(wei_to_int(balance))})"
            )
        elif amount > max_amount:
            raise ExecutionError(f"Max transaction amount {humanify_number(wei_to_int(max_amount))}")
        elif amount < min_amount:
            raise ExecutionError(f"Min transaction amount {humanify_number(wei_to_int(min_amount))}")

    def calculate_amount_base(self, balance):
        if self.leave_balance:
            if balance < int_to_wei(float(self.leave_balance_amount)):
                raise ExecutionError(
                    f"Not enough balance. Balance < Leave Balance ({humanify_number(wei_to_int(balance))} < {self.leave_balance_amount})"
                )
            else:
                amount = balance - int_to_wei(float(self.leave_balance_amount))
        else:
            amount = int_to_wei(float(self.amount))

        return amount

    def get_contract_txn(self):
        raise NotImplementedError

    def bridge(self):
        try:
            scan = self.configs["chains"][self.from_chain]["scan"]

            contract_txn = self.get_contract_txn()

            if debug_mode():
                logger.info(
                    f"{get_tx_link(scan, '0x2c9a0daa5b71d618abc0d275bea252071f705bed8ccbcaa670fc1c0a40d117e2')}"
                )
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(self.calculated_amount))} | Bridge successful"
                )
                return True

            private_key = get_private_key(self.web3, self.secrets, self.address)
            tx_hash = sign_tx(self.web3, contract_txn, private_key)

            logger.info(f"{get_tx_link(scan, tx_hash)}")

            if wait_tx_completion(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(self.calculated_amount))} | Bridge successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(self.calculated_amount))} | Bridge unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls, bridge):
        instructions = load_json(f"modules/bridge/{bridge}/instructions.json")
        secrets = load_json(f"modules/bridge/{bridge}/secrets.json")
        configs = load_json("../configs.json")

        addresses = instructions["addresses"]
        amounts = zip_to_addresses(addresses, instructions["amounts"])

        rpc = random.choice(configs["chains"][instructions["from_chain"]]["rpcs"])
        web3 = Web3(Web3.HTTPProvider(rpc))

        if instructions["randomize"]:
            random.shuffle(addresses)

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            amount = None if instructions["leave_balance"] else amounts[address]
            result = cls(
                secrets,
                configs,
                instructions["leave_balance"],
                instructions["leave_balance_amount"],
                amount,
                address,
                instructions["from_chain"],
                instructions["to_chain"],
                instructions["symbol"],
                web3,
            ).bridge()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {humanify_seconds(sleep_time)}")
                sleep(sleep_time)
