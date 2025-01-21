import ccxt
import random

from utils import load_json, log_error, round_number, debug_mode, sleep, logger
from core.helpers import zip_to_addresses, prettify_seconds, prettify_number


class WithdrawBase:
    def __init__(
        self,
        cex,
        secrets,
        address,
        chain,
        symbol,
        amount_includes_fee,
        amount,
    ):
        self.secrets = secrets
        self.address = address
        self.chain = chain
        self.symbol = symbol
        self.amount_includes_fee = amount_includes_fee
        self.amount = amount
        self.exchange = ccxt.__dict__[cex](self.cex_details())
        self._withdraw_params = None

    def cex_details(self):
        return {
            "apiKey": self.secrets["api_key"],
            "secret": self.secrets["api_secret"],
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }

    def withdraw_params(self):
        raise NotImplementedError

    def calculate_fee(self):
        raise NotImplementedError

    def calculate_amount(self):
        amount = float(self.amount)

        if self.amount_includes_fee:
            amount = amount - float(self.calculate_fee())

        return round_number(amount)

    def withdraw(self):
        try:
            self.calculated_amount = self.calculate_amount()

            if debug_mode():
                logger.success(
                    f"{self.address} | {self.symbol} | {prettify_number(self.calculated_amount)} | Withdrawal successful"
                )
                return True

            self.exchange.withdraw(
                code=self.symbol,
                amount=self.calculated_amount,
                address=self.address,
                tag=None,
                params=self.withdraw_params(),
            )

            logger.success(
                f"{self.address} | {self.symbol} | {prettify_number(self.calculated_amount)} | Withdrawal successful"
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
                logger.info(f"Sleeping for {prettify_seconds(sleep_time)}")
                sleep(sleep_time)
