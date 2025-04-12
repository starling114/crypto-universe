import random
import time
from hexbytes import HexBytes

from utils import (
    load_json,
    int_to_wei,
    wei_to_int,
    log_error,
    debug_mode,
    sleep,
    logger,
    ExecutionError,
    NULL_TOKEN_ADDRESS,
)
from core.helpers import (
    calculate_token_balance,
    calculate_base_amount,
    transaction_data,
    approve_token,
    send_transaction,
    verify_transaction,
    estimate_gas,
    estimate_gas_price,
    execute_amount_validations,
    get_private_key,
    get_transaction_link,
    zip_to_objects,
    prettify_seconds,
    prettify_number,
)
from core.models.helpers import build_token, build_chain, build_web3, build_contract
from modules.swap.pancakeswap.helpers import (
    ROUTER_ABI,
    ROUTER_CONTRACT_ADDRESS,
    QUOTER_ABI,
    QUOTER_CONTRACT_ADDRESS,
    FACTORY_CONTRACT_ADDRESS,
    FACTORY_ABI,
    V2_ROUTER_ABI,
    V2_ROUTER_CONTRACT_ADDRESS,
)

# PancakeSwap specific constants
FEE_TIER = 2500  # 0.25% fee tier
SLIPPAGE = 50  # 0.5% slippage


class SwapPancakeswap:
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
        self.address = address
        self.chain = chain
        self.web3 = web3
        self.from_token = from_token
        self.to_token = to_token
        self.amount_includes_fee = amount_includes_fee

        self.quoter_contract = build_contract(self.web3, QUOTER_CONTRACT_ADDRESS, QUOTER_ABI)
        self.router_contract = build_contract(self.web3, ROUTER_CONTRACT_ADDRESS, ROUTER_ABI)
        self.v2_router_contract = build_contract(self.web3, V2_ROUTER_CONTRACT_ADDRESS, V2_ROUTER_ABI)
        self.factory_contract = build_contract(self.web3, FACTORY_CONTRACT_ADDRESS, FACTORY_ABI)

    def pre_checks(self):
        if self.from_token.is_native() or self.to_token.is_native():
            raise ExecutionError("Native tokens are not supported")

    def check_pool(self):
        pool = self.factory_contract.functions.getPool(self.from_token.address, self.to_token.address, FEE_TIER).call()

        logger.info(pool)

        if pool == NULL_TOKEN_ADDRESS:
            raise ExecutionError(
                f"Pool not found for {self.from_token.symbol} -> {self.to_token.symbol}. Please check the token addresses."
            )

    def get_min_amount_out(self, amount):
        quote_data = self.quoter_contract.functions.quoteExactInputSingle(
            (self.from_token.address, self.to_token.address, amount, FEE_TIER, 0)
        ).call()

        return int(quote_data[0] - (quote_data[0] / 100 * SLIPPAGE))

    def calculate_amount(self):
        balance = calculate_token_balance(self.web3, self.address, self.from_token)
        amount = calculate_base_amount(balance, self.amount, self.leave_balance, self.leave_balance_amount)

        if self.amount_includes_fee and self.from_token.is_native():
            amount = amount - self.calculate_fee()

        execute_amount_validations(balance, amount)

        return amount

    # https://github.com/RetributionByRevenue/pancakeswapV3_simple_swap/blob/main/main.py
    # https://docs.pancakeswap.finance/developers/smart-contracts/pancakeswap-exchange/v3-contracts
    # https://github.com/NeuralTechnologies/PancakeMMbot/blob/main/const.py
    # https://github.com/czbag/base/blob/e0558d094e608dd7eefae4aa789898f6fe7306f6/config.py#L119
    def swap(self):
        try:
            logger.info(f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | Swap started")

            self.pre_checks()

            calculated_amount = self.calculate_amount()
            min_amount_out = self.get_min_amount_out(calculated_amount)

            # if debug_mode():
            #     logger.info(f"{get_transaction_link(self.chain, 'DEBUG')}")
            #     logger.success(
            #         f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | {prettify_number(wei_to_int(calculated_amount))} | Swap successful"
            #     )
            #     return True

            private_key = get_private_key(self.web3, self.address, self.secrets)

            approve_token(
                self.web3, self.from_token, calculated_amount, self.router_contract.address, self.address, private_key
            )

            # approve_token(
            #     self.web3,
            #     self.from_token,
            #     calculated_amount,
            #     self.v2_router_contract.address,
            #     self.address,
            #     private_key,
            # )

            # path = [self.from_token.address, self.to_token.address]
            # deadline = int(time.time()) + 600  # 10 minutes
            # amounts_out = self.v2_router_contract.functions.getAmountsOut(calculated_amount, path).call()

            # min_amount_out = int(amounts_out[-1] - (amounts_out[-1] / 100 * SLIPPAGE))

            # tx_pre_data = transaction_data(self.web3, from_address=self.address)
            # tx_pre_data["gasPrice"] = estimate_gas_price(self.web3)
            # tx_pre_data["gas"] = estimate_gas(self.web3, tx_pre_data)

            # tx_data = self.v2_router_contract.functions.swapExactTokensForETH(
            #     calculated_amount, min_amount_out, path, self.web3.to_checksum_address(self.address), deadline
            # ).build_transaction(tx_pre_data)

            deadline = int(time.time()) + 30  # Tweak deadline
            tx_pre_data = transaction_data(self.web3, from_address=self.address)
            tx_pre_data["gasPrice"] = estimate_gas_price(self.web3)
            tx_pre_data["gas"] = estimate_gas(self.web3, tx_pre_data)

            # tx_data = self.router_contract.functions.exactInputSingle(
            #     {
            #         "tokenIn": self.from_token.address,
            #         "tokenOut": self.to_token.address,
            #         "fee": FEE_TIER,
            #         "recipient": self.web3.to_checksum_address(self.address),
            #         "deadline": deadline,
            #         "amountIn": calculated_amount,
            #         "amountOutMinimum": min_amount_out,
            #         "sqrtPriceLimitX96": 0,
            #     }
            # ).build_transaction(tx_pre_data)

            # swap_data = self.router_contract.encodeABI(
            #     fn_name="exactInputSingle",
            #     args=[
            #         (
            #             self.from_token.address,
            #             self.to_token.address,
            #             FEE_TIER,
            #             self.web3.to_checksum_address(self.address),
            #             deadline,
            #             min_amount_out,
            #             0,
            #         )
            #     ],
            # )

            # tx_data = self.router_contract.functions.multicall(deadline, [swap_data]).build_transaction(tx_pre_data)

            from_token_bytes = HexBytes(self.from_token.address).rjust(20, b"\0")
            to_token_bytes = HexBytes(self.to_token.address).rjust(20, b"\0")
            fee_bytes = (FEE_TIER).to_bytes(3, "big")

            path = from_token_bytes + fee_bytes + to_token_bytes

            swap_data = self.router_contract.encodeABI(
                fn_name="exactInput",
                args=[
                    (
                        path,
                        self.to_token.address,
                        calculated_amount,
                        min_amount_out,
                    )
                ],
            )

            full_data = [swap_data]

            tx_data = self.router_contract.functions.multicall(full_data).build_transaction(tx_pre_data)

            logger.info(f"Transaction data: {tx_data}")

            tx_hash = send_transaction(self.web3, tx_data, private_key, include_fees=False)

            if verify_transaction(self.web3, tx_hash):
                logger.success(
                    f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | "
                    f"{prettify_number(wei_to_int(calculated_amount))} | Swap successful"
                )
                return True
            else:
                logger.error(
                    f"{self.address} | {self.from_token.symbol}->{self.to_token.symbol} | "
                    f"{prettify_number(wei_to_int(calculated_amount))} | Swap unsuccessful"
                )
                return False

        except Exception as e:
            log_error(e, self.address)
            return False

    @classmethod
    def run(cls):
        logger.error("PancakeSwap module is broken...")
        instructions = load_json("modules/swap/pancakeswap/instructions.json")
        secrets = load_json("modules/swap/pancakeswap/secrets.json")

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
