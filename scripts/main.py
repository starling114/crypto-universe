from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("../.env"))
import sys
from modules import *
from utils import log_error, logger, import_premium_module, run_module, run_premium_module

MODULES = {
    "withdraw-okx": WithdrawOkx,
    "bridge-relay": BridgeRelay,
    "bridge-hyperlane": BridgeHyperlane,
    "swap-jumper": SwapJumper,
    "transfer": Transfer,
    "yt_tokens": YtTokens,
    "testnet-mitosis": TestnetMitosis,
}
PREMIUM_MODULES = {
    "premium/sale-fjord": import_premium_module("sale_fjord", "SaleFjord"),
}

if __name__ == "__main__":
    try:
        if len(sys.argv) <= 1:
            logger.error(
                "Console mode is not supported, please run via `npm start` from root folder. See details in README.md."
            )
        else:
            aaarg = sys.argv[1]

            if "premium/" in aaarg:
                run_premium_module(aaarg, PREMIUM_MODULES)
            else:
                run_module(aaarg, MODULES)
    except KeyboardInterrupt:
        logger.info("Execution stopped.")
    except Exception as e:
        log_error(e)
        # raise e
