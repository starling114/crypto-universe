from web3 import Web3
import time
import random
from utils import (
    load_json,
    humanify_seconds,
    humanify_number,
    get_tx_link,
    zip_to_addresses,
    log_error,
    get_token_data,
    get_private_key,
    get_balance,
    int_to_wei,
    wei_to_int,
    get_transactions_count,
    get_gas_limit,
    get_gas_price,
    sign_tx,
    wait_tx_completion,
    debug_mode,
    ExecutionError,
)
from utils import logger

NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
TRANSFER_MIN_TRANSACTION_AMOUNT = 0.00005


class Transfer:
    def __init__(
        self,
        secrets,
        configs,
        leave_balance,
        leave_balance_amount,
        source_address,
        amount,
        destinaion_address,
        use_custom_asset,
        custom_asset,
        chain,
        symbol,
        web3,
    ):
        self.secrets = secrets
        self.configs = configs
        self.leave_balance = leave_balance
        self.leave_balance_amount = leave_balance_amount
        self.source_address = source_address
        self.amount = amount
        self.destinaion_address = destinaion_address
        self.use_custom_asset = use_custom_asset
        self.custom_asset = custom_asset
        self.chain = chain
        self.symbol = symbol
        self.web3 = web3

    def calculate_token_data(self):
        if self.use_custom_asset:
            address, contract, decimals, symbol = get_token_data(
                self.web3, self.custom_asset
            )
        else:
            config_address = self.configs["chains"][self.chain]["tokens"][self.symbol]

            if config_address == "":
                address = NATIVE_TOKEN_ADDRESS
                contract = None
                decimals = 18
                symbol = self.symbol
            else:
                address, contract, decimals, symbol = get_token_data(
                    self.web3, config_address
                )

        return [address, contract, decimals, symbol]

    def calculate_amount(self, token_address, token_contract, decimals):
        amount = 0

        if token_address == NATIVE_TOKEN_ADDRESS:
            balance = get_balance(self.web3, self.source_address)
        else:
            balance = get_balance(self.web3, self.source_address, token_contract)

        if self.leave_balance:
            if balance < int_to_wei(float(self.leave_balance_amount), decimals):
                raise ExecutionError(
                    f"Not enough balance. Balance < Leave Balance ({humanify_number(wei_to_int(balance, decimals))} < {self.leave_balance_amount})"
                )
            else:
                amount = balance - int_to_wei(
                    float(self.leave_balance_amount), decimals
                )
        else:
            amount = int_to_wei(float(self.amount), decimals)

        min_transaction_amount = int_to_wei(TRANSFER_MIN_TRANSACTION_AMOUNT, decimals)
        if amount > balance:
            raise ExecutionError(
                f"Not enough balance. Amount > Balance ({humanify_number(wei_to_int(amount, decimals))} > {humanify_number(wei_to_int(balance, decimals))})"
            )
        elif amount < min_transaction_amount:
            raise ExecutionError(
                f"Min transaction amount {humanify_number(wei_to_int(min_transaction_amount, decimals))}"
            )
        else:
            return amount

    def transfer(self):
        try:
            scan = self.configs["chains"][self.chain]["scan"]

            token_address, token_contract, decimals, symbol = (
                self.calculate_token_data()
            )
            calculated_amount = self.calculate_amount(
                token_address, token_contract, decimals
            )

            if token_address == NATIVE_TOKEN_ADDRESS:
                contract_txn = {
                    "from": self.web3.to_checksum_address(self.source_address),
                    "nonce": get_transactions_count(self.web3, self.source_address),
                    "value": calculated_amount,
                    "to": self.web3.to_checksum_address(self.destinaion_address),
                    "chainId": self.web3.eth.chain_id,
                    "gas": 0,
                    "gasPrice": 0,
                }

            else:
                contract_txn = token_contract.functions.transfer(
                    Web3.to_checksum_address(
                        self.web3.to_checksum_address(self.source_address)
                    ),
                    calculated_amount,
                ).build_transaction(
                    {
                        "from": self.web3.to_checksum_address(self.source_address),
                        "chainId": self.web3.eth.chain_id,
                        "nonce": get_transactions_count(self.web3, self.source_address),
                        "gas": 0,
                        "gasPrice": 0,
                    }
                )

            contract_txn["gas"] = get_gas_limit(self.web3, contract_txn)
            contract_txn["gasPrice"] = get_gas_price(self.web3)

            # In case of transfer max in native token gas should be deducted from amount
            if (
                token_address == NATIVE_TOKEN_ADDRESS
                and self.leave_balance
                and int(self.leave_balance_amount) == 0
            ):
                gas_estimate = int(contract_txn["gasPrice"] * contract_txn["gas"])
                contract_txn["value"] = calculated_amount - gas_estimate

            if debug_mode():
                logger.info(
                    f"{get_tx_link(scan, '0x2c9a0daa5b71d618abc0d275bea252071f705bed8ccbcaa670fc1c0a40d117e2')}"
                )
                logger.success(
                    f"{self.source_address} | {symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Transfer successful"
                )
                return True

            private_key = get_private_key(self.web3, self.secrets, self.source_address)
            tx_hash = sign_tx(self.web3, contract_txn, private_key)

            logger.info(f"{get_tx_link(scan, tx_hash)}")

            if wait_tx_completion(self.web3, tx_hash):
                logger.success(
                    f"{self.source_address} | {symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Transfer successful"
                )
                return True
            else:
                logger.error(
                    f"{self.source_address} | {symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Transfer unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.source_address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/transfer/instructions.json")
        secrets = load_json("modules/transfer/secrets.json")
        configs = load_json("../configs.json")

        source_addresses = instructions["source_addresses"]
        amounts = zip_to_addresses(source_addresses, instructions["amounts"])
        destinaion_addresses = zip_to_addresses(
            source_addresses, instructions["destinaion_addresses"]
        )

        rpc = random.choice(configs["chains"][instructions["chain"]]["rpcs"])
        web3 = Web3(Web3.HTTPProvider(rpc))

        if instructions["randomize"]:
            random.shuffle(source_addresses)

        last_address = len(source_addresses) - 1
        for index, source_address in enumerate(source_addresses):
            amount = None if instructions["leave_balance"] else amounts[source_address]
            result = cls(
                secrets,
                configs,
                instructions["leave_balance"],
                instructions["leave_balance_amount"],
                source_address,
                amount,
                destinaion_addresses[source_address],
                instructions["use_custom_asset"],
                instructions["custom_asset"],
                instructions["chain"],
                instructions["symbol"],
                web3,
            ).transfer()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {humanify_seconds(sleep_time)}")
                time.sleep(sleep_time)
