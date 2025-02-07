import random

from utils import post_call, load_json, int_to_wei, wei_to_int, log_error, debug_mode, sleep, logger, ExecutionError
from core.helpers import (
    calculate_token_balance,
    calculate_base_amount,
    transaction_data,
    approve_token,
    send_transaction,
    verify_transaction,
    estimate_gas,
    execute_amount_validations,
    get_private_key,
    get_transaction_link,
    zip_to_objects,
    prettify_seconds,
    prettify_number,
)
from core.models.helpers import build_token, build_chain, build_web3
from modules.swap.jumper.helpers import MAX_SLIPPAGE, SIMULATE_AMOUNT


class SwapJumper:
    def __init__(
        self,
        secrets,
        leave_balance,
        leave_balance_amount,
        amount,
        address,
        chain,
        web3,
        from_token,
        to_token,
        amount_includes_fee,
    ):
        self.secrets = secrets
        self.leave_balance = leave_balance
        self.leave_balance_amount = leave_balance_amount
        self.amount = amount
        self.address = address
        self.chain = chain
        self.web3 = web3
        self.from_token = from_token
        self.to_token = to_token
        self.amount_includes_fee = amount_includes_fee

    def get_remote_data(self, amount):
        headers = {"X-Lifi-Sdk": "3.0.0-alpha.57", "X-Lifi-Widget": "3.0.0-alpha.35"}
        params = {
            "fromAddress": self.address,
            "fromAmount": str(amount),
            "fromChainId": self.chain.chain_id,
            "fromTokenAddress": self.from_token.address,
            "toAddress": self.address,
            "toChainId": self.chain.chain_id,
            "toTokenAddress": self.to_token.address,
            "options": {
                "integrator": "jumper.exchange",
                "order": "CHEAPEST",
                "slippage": MAX_SLIPPAGE / 100,
                "maxPriceImpact": 1,
                "allowSwitchChain": False,
                "insurance": False,
            },
        }
        route_data = post_call("https://li.quest/v1/advanced/routes", headers=headers, json=params)

        if len(route_data["routes"]) <= 0:
            raise ExecutionError("No swap routes found")

        data = post_call(
            "https://li.quest/v1/advanced/stepTransaction", headers=headers, json=route_data["routes"][0]["steps"][0]
        )

        return data["transactionRequest"]

    def calculate_fee(self):
        simulate_amount = int_to_wei(SIMULATE_AMOUNT)
        data = self.get_remote_data(simulate_amount)
        value = int(data["value"], 16)
        tx_data = transaction_data(
            self.web3, from_address=self.address, to_address=data["to"], data=data["data"], value=value
        )
        gas_fee = estimate_gas(self.web3, tx_data) * tx_data["gasPrice"]
        jumper_fee = value - simulate_amount
        return gas_fee + jumper_fee

    def calculate_amount(self):
        balance = calculate_token_balance(self.web3, self.address, self.from_token)
        amount = calculate_base_amount(balance, self.amount, self.leave_balance, self.leave_balance_amount)

        if self.amount_includes_fee and self.from_token.is_native():
            amount = amount - self.calculate_fee()

        execute_amount_validations(balance, amount)

        return amount

    def swap(self):
        try:
            logger.info(f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | Swap started")

            calculated_amount = self.calculate_amount()
            remote_data = self.get_remote_data(calculated_amount)
            remote_value = int(remote_data["value"], 16)

            if debug_mode():
                logger.info(f"{get_transaction_link(self.chain, 'DEBUG')}")
                logger.success(
                    f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | {prettify_number(wei_to_int(calculated_amount))} | Swap successful"
                )
                return True

            private_key = get_private_key(self.web3, self.secrets, self.address)

            approve_token(self.web3, self.from_token, calculated_amount, remote_data["to"], self.address, private_key)

            tx_data = transaction_data(self.web3, self.address, remote_data["to"], remote_data["data"], remote_value)
            tx_hash = send_transaction(self.web3, tx_data, private_key)

            logger.info(f"{get_transaction_link(self.chain, tx_hash)}")

            if verify_transaction(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | {prettify_number(wei_to_int(calculated_amount))} | Swap successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | {prettify_number(wei_to_int(calculated_amount))} | Swap unsuccessful"
                )
                return False
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls):
        instructions = load_json("modules/swap/jumper/instructions.json")
        secrets = load_json("modules/swap/jumper/secrets.json")

        addresses = instructions["addresses"]
        amounts = zip_to_objects(addresses, instructions["amounts"])

        if instructions["randomize"]:
            random.shuffle(addresses)

        chain = build_chain(instructions["chain"])
        web3 = build_web3(chain)

        if instructions["use_custom_symbols"]:
            from_token = build_token(web3, token_address=instructions["custom_from_symbol"])
            to_token = build_token(web3, token_address=instructions["custom_to_symbol"])
        else:
            from_token = build_token(web3, chain=chain, symbol=instructions["from_symbol"])
            to_token = build_token(web3, chain=chain, symbol=instructions["to_symbol"])

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            amount = None if instructions["leave_balance"] else amounts[address]
            result = cls(
                secrets,
                instructions["leave_balance"],
                instructions["leave_balance_amount"],
                amount,
                address,
                chain,
                web3,
                from_token,
                to_token,
                instructions["amount_includes_fee"],
            ).swap()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {prettify_seconds(sleep_time)}")
                sleep(sleep_time)
