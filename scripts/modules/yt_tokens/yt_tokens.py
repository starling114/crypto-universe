from web3 import Web3
import random
from utils import load_json, get_call, log_error, int_to_wei, wei_to_int, debug_mode, sleep, ExecutionError
from utils import logger

from core.helpers import (
    calculate_token_balance,
    transaction_data,
    send_transaction,
    verify_transaction,
    execute_amount_validations,
    get_private_key,
    get_transaction_link,
    zip_to_objects,
    prettify_seconds,
    prettify_number,
)
from core.models.helpers import build_token, build_chain, build_web3
from modules.yt_tokens.helpers import DEFAULT_SLIPPAGE


class YtTokens:
    def __init__(
        self,
        secrets,
        chain,
        token,
        yt_token,
        yt_token_market_address,
        max_ethereum_gas_price,
        address,
        amount,
        web3,
    ):
        self.secrets = secrets
        self.chain = chain
        self.token = token
        self.yt_token = yt_token
        self.yt_token_market_address = yt_token_market_address
        self.max_ethereum_gas_price = int(max_ethereum_gas_price)
        self.address = address
        self.amount = amount
        self.web3 = web3

    def check_yt_token_balance(self):
        balance = calculate_token_balance(self.web3, self.address, self.yt_token, check_balance=False)

        if balance > 0:
            raise ExecutionError(
                f"YT token is already present ({prettify_number(wei_to_int(balance, self.yt_token.decimals))} {self.yt_token.symbol})"
            )

    def calculate_amount(self):
        balance = calculate_token_balance(self.web3, self.address, self.token)
        amount = int_to_wei(float(self.amount))

        execute_amount_validations(balance, amount)

        return amount

    def get_remote_data(self, amount):
        params = {
            "receiver": self.address,
            "slippage": DEFAULT_SLIPPAGE,
            "enableAggregator": "true",
            "tokenIn": self.token.address,
            "tokenOut": self.yt_token.address,
            "amountIn": amount,
        }

        return get_call(
            f"https://api-v2.pendle.finance/core/v1/sdk/{self.web3.eth.chain_id}/markets/{self.yt_token_market_address}/swap",
            params=params,
        )

    def swap(self):
        try:
            self.check_yt_token_balance()

            calculated_amount = self.calculate_amount()

            remote_tx_data = self.get_remote_data(calculated_amount)["tx"]

            private_key = get_private_key(self.web3, self.secrets, self.address)
            tx_data = transaction_data(
                self.web3,
                from_address=remote_tx_data["from"],
                to_address=remote_tx_data["to"],
                data=remote_tx_data["data"],
                value=int(remote_tx_data["value"]),
            )
            if self.web3.eth.chain_id == 1 and tx_data["gasPrice"] > Web3.to_wei(self.max_ethereum_gas_price, "gwei"):
                logger.error(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Gas price exceeds limit of {self.max_ethereum_gas_price} Gwei"
                )
                return False

            if debug_mode():
                logger.info(f"{get_transaction_link(self.chain, 'DEBUG')}")
                logger.success(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Swap successful"
                )
                return True

            tx_hash = send_transaction(self.web3, tx_data, private_key)

            logger.info(f"{get_transaction_link(self.chain, tx_hash)}")

            if verify_transaction(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Swap successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.token.symbol} | {prettify_number(wei_to_int(calculated_amount, self.token.decimals))} | Swap unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/yt_tokens/instructions.json")
        secrets = load_json("modules/yt_tokens/secrets.json")

        addresses = instructions["addresses"]
        amounts = zip_to_objects(addresses, instructions["amounts"])

        if instructions["randomize"]:
            random.shuffle(addresses)

        chain = build_chain(instructions["chain"])
        web3 = build_web3(chain)

        token = build_token(web3, chain=chain, symbol=instructions["symbol"])
        yt_token = build_token(web3, token_address=instructions["yt_token"]["address"])

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            result = cls(
                secrets,
                chain,
                token,
                yt_token,
                instructions["yt_token"]["market_address"],
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
                logger.info(f"Sleeping for {prettify_seconds(sleep_time)}")
                sleep(sleep_time)
