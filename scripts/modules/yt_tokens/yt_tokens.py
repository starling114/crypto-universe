from web3 import Web3
import random
from utils import (
    NULL_TOKEN_ADDRESS,
    load_json,
    humanify_seconds,
    humanify_number,
    get_call,
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
    sleep,
    ExecutionError,
)
from utils import logger

DEFAULT_SLIPPAGE = 0.002


class YtTokens:
    def __init__(
        self,
        configs,
        secrets,
        chain,
        symbol,
        yt_token,
        max_ethereum_gas_price,
        address,
        amount,
        web3,
    ):
        self.configs = configs
        self.secrets = secrets
        self.chain = chain
        self.symbol = symbol
        self.yt_token = yt_token
        self.max_ethereum_gas_price = int(max_ethereum_gas_price)
        self.address = address
        self.amount = amount
        self.web3 = web3

    def calculate_yt_token_data(self):
        address, contract, decimals, symbol = get_token_data(self.web3, self.yt_token["address"])

        return [address, contract, decimals, symbol]

    def check_yt_token_balance(self, token_contract, decimals, symbol):
        balance = get_balance(self.web3, self.address, token_contract)

        if balance > 0:
            raise ExecutionError(
                f"YT token is already present ({humanify_number(wei_to_int(balance, decimals))} {symbol})"
            )

    def calculate_token_data(self):
        config_address = self.configs["chains"][self.chain]["tokens"][self.symbol]

        if config_address == "":
            address = NULL_TOKEN_ADDRESS
            contract = None
            decimals = 18
            symbol = self.symbol
        else:
            address, contract, decimals, symbol = get_token_data(self.web3, config_address)

        return [address, contract, decimals, symbol]

    def calculate_amount(self, decimals):
        balance = get_balance(self.web3, self.address)
        amount = int_to_wei(float(self.amount), decimals)

        if amount >= balance:
            raise ExecutionError(
                f"Not enough balance. Amount > Balance ({humanify_number(wei_to_int(amount, decimals))} >= {humanify_number(wei_to_int(balance, decimals))})"
            )
        else:
            return amount

    def get_data(self, token_address, yt_token_address, amount):
        params = {
            "receiver": self.address,
            "slippage": DEFAULT_SLIPPAGE,
            "enableAggregator": "true",
            "tokenIn": token_address,
            "tokenOut": yt_token_address,
            "amountIn": amount,
        }

        return get_call(
            f"https://api-v2.pendle.finance/core/v1/sdk/{self.web3.eth.chain_id}/markets/{self.yt_token['market_address']}/swap",
            params=params,
        )

    def swap(self):
        try:
            scan = self.configs["chains"][self.chain]["scan"]

            yt_token_address, yt_token_contract, yt_token_decimals, yt_token_symbol = self.calculate_yt_token_data()
            self.check_yt_token_balance(yt_token_contract, yt_token_decimals, yt_token_symbol)

            token_address, _, decimals, _ = self.calculate_token_data()
            calculated_amount = self.calculate_amount(decimals)

            tx_data = self.get_data(token_address, yt_token_address, calculated_amount)
            transaction_data = tx_data["tx"]

            contract_txn = {
                "from": self.web3.to_checksum_address(transaction_data["from"]),
                "nonce": get_transactions_count(self.web3, self.address),
                "value": int(transaction_data["value"]),
                "to": self.web3.to_checksum_address(transaction_data["to"]),
                "data": transaction_data["data"],
                "chainId": self.web3.eth.chain_id,
                "gas": 0,
                "gasPrice": 0,
            }
            contract_txn["gas"] = get_gas_limit(self.web3, contract_txn)
            contract_txn["gasPrice"] = get_gas_price(self.web3)

            if self.web3.eth.chain_id == 1 and contract_txn["gasPrice"] > Web3.to_wei(
                self.max_ethereum_gas_price, "gwei"
            ):
                logger.error(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Gas price exceeds limit of {self.max_ethereum_gas_price} Gwei"
                )
                return False

            if debug_mode():
                logger.info(f"{get_tx_link(scan, 'DEBUG')}")
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Swap successful"
                )
                return True

            private_key = get_private_key(self.web3, self.secrets, self.address)
            tx_hash = sign_tx(self.web3, contract_txn, private_key)

            logger.info(f"{get_tx_link(scan, tx_hash)}")

            if wait_tx_completion(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Swap successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.symbol} | {humanify_number(wei_to_int(calculated_amount, decimals))} | Swap unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/yt_tokens/instructions.json")
        secrets = load_json("modules/yt_tokens/secrets.json")
        configs = load_json("../configs.json")

        addresses = instructions["addresses"]
        amounts = zip_to_addresses(addresses, instructions["amounts"])

        rpc = random.choice(configs["chains"][instructions["chain"]]["rpcs"])
        web3 = Web3(Web3.HTTPProvider(rpc))

        if instructions["randomize"]:
            random.shuffle(addresses)

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            result = cls(
                configs,
                secrets,
                instructions["chain"],
                instructions["symbol"],
                instructions["yt_token"],
                instructions["max_ethereum_gas_price"],
                address,
                amounts[address],
                web3,
            ).swap()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {humanify_seconds(sleep_time)}")
                sleep(sleep_time)
