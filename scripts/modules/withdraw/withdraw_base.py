import ccxt
import random

from utils import (
    load_json,
    humanify_seconds,
    humanify_number,
    round_number,
    zip_to_addresses,
    log_error,
    debug_mode,
    sleep,
)
from utils import logger


class WithdrawBase:
    def __init__(
        self,
        cex,
        secrets,
        address,
        network,
        symbol,
        amount_includes_fee,
        amount,
    ):
        self.secrets = secrets
        self.address = address
        self.network = network
        self.symbol = symbol
        self.amount_includes_fee = amount_includes_fee
        self.amount = amount
        self.exchange = self.get_ccxt(cex)

    def get_ccxt(self, cex):
        cex_details = {
            "apiKey": self.secrets["api_key"],
            "secret": self.secrets["api_secret"],
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }

        if cex in ["okx"]:
            cex_details["password"] = self.secrets["password"]

        return ccxt.__dict__[cex](cex_details)

    def params(self):
        return {"network": self.network}

    def calculate_amount(self, fee):
        if self.amount_includes_fee:
            return round_number(float(self.amount) - float(fee))
        else:
            return round_number(float(self.amount))

    def withdraw(self):
        try:
            params = self.params()
            calculated_amount = self.calculate_amount(params["fee"])

            if debug_mode():
                logger.success(
                    f"{self.address} | {self.symbol} | {humanify_number(calculated_amount)} | Withdrawal successful"
                )
                return True

            self.exchange.withdraw(
                code=self.symbol,
                amount=calculated_amount,
                address=self.address,
                tag=None,
                params=params,
            )

            logger.success(
                f"{self.address} | {self.symbol} | {humanify_number(calculated_amount)} | Withdrawal successful"
            )

            return True
        except Exception as e:
            log_error(e, self.address)

            return False

    @classmethod
    def run(cls, cex):
        instructions = load_json(f"modules/withdraw/{cex}/instructions.json")
        secrets = load_json(f"modules/withdraw/{cex}/secrets.json")

        addresses = instructions["addresses"]
        amounts = zip_to_addresses(addresses, instructions["amounts"])

        if instructions["randomize"]:
            random.shuffle(addresses)

        last_address = len(addresses) - 1
        for index, address in enumerate(addresses):
            result = cls(
                cex,
                secrets,
                address,
                instructions["chain"],
                instructions["symbol"],
                instructions["amount_includes_fee"],
                amounts[address],
            ).withdraw()

            if index != last_address and instructions["sleep"] and result:
                sleep_time = random.randint(
                    int(instructions["sleep_delays"][0]),
                    int(instructions["sleep_delays"][1]),
                )
                logger.info(f"Sleeping for {humanify_seconds(sleep_time)}")
                sleep(sleep_time)
