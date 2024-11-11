from web3 import Web3
import time
import random

from utils import (
    load_json,
    int_to_wei,
    post_call,
    wei_to_int,
    get_balance,
    get_transactions_count,
    get_gas_price,
    get_gas_limit,
    sign_tx,
    zip_to_addresses,
    humanify_seconds,
    humanify_number,
    get_private_key,
    get_tx_link,
    wait_tx_completion,
    log_error,
    ExecutionError,
)
from utils import logger

RELAY_MIN_TRANSACTION_AMOUNT = 0.00005
NULL_TOKEN_ADDRESS = "0x0000000000000000000000000000000000000000"


class BridgeRelay:
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
        self.address = address
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.symbol = symbol
        self.web3 = web3

    def get_data(self, amount):
        # TODO: Change NULL_TOKEN_ADDRESS to symbol address to support other tokens
        params = {
            "user": self.address,
            "recipient": self.address,
            "originChainId": self.configs["chains"][self.from_chain]["chain_id"],
            "destinationChainId": self.configs["chains"][self.to_chain]["chain_id"],
            "originCurrency": NULL_TOKEN_ADDRESS,
            "destinationCurrency": NULL_TOKEN_ADDRESS,
            "amount": str(amount),
            "tradeType": "EXACT_INPUT",
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
        }

        return post_call("https://api.relay.link/quote", json=params)

    def calculate_amount(self):
        amount = 0
        balance = get_balance(self.web3, self.address)

        if self.leave_balance:
            if balance < int_to_wei(float(self.leave_balance_amount)):
                raise ExecutionError(
                    f"Not enough balance. Balance < Leave Balance ({humanify_number(wei_to_int(balance))} < {self.leave_balance_amount})"
                )
            else:
                amount = balance - int_to_wei(float(self.leave_balance_amount))
        else:
            amount = int_to_wei(float(self.amount))

        min_transaction_amount = int_to_wei(RELAY_MIN_TRANSACTION_AMOUNT)
        if amount > balance:
            raise ExecutionError(
                f"Not enough balance. Amount > Balance ({humanify_number(wei_to_int(amount))} > {humanify_number(wei_to_int(balance))})"
            )
        elif amount < min_transaction_amount:
            raise ExecutionError(
                f"Min transaction amount {humanify_number(wei_to_int(min_transaction_amount))}"
            )
        else:
            return amount

    def bridge(self):
        try:
            scan = self.configs["chains"][self.from_chain]["scan"]
            private_key = get_private_key(self.web3, self.secrets, self.address)

            calculated_amount = self.calculate_amount()

            tx_data = self.get_data(calculated_amount)
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

            logger.info(
                f"{get_tx_link(scan, '0x2c9a0daa5b71d618abc0d275bea252071f705bed8ccbcaa670fc1c0a40d117e2')}"
            )
            logger.success(
                f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount))} | Bridge successful"
            )
            return True

            tx_hash = sign_tx(self.web3, contract_txn, private_key)

            logger.info(
                f"{get_tx_link(scan, tx_hash)}"
            )

            if wait_tx_completion(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount))} | Bridge successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount))} | Bridge unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/bridge/relay/instructions.json")
        secrets = load_json("modules/bridge/relay/secrets.json")
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
                time.sleep(sleep_time)
