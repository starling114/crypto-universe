from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv("../.env"))
import sys
from modules import *
from utils import log_error, logger

MODULES = {
    "withdraw-okx": WithdrawOkx,
    "bridge-relay": BridgeRelay,
    "bridge-hyperlane": BridgeHyperlane,
    "transfer": Transfer,
    "testnet-mitosis": TestnetMitosis,
}


def extract_from_args():
    aaarg = sys.argv[1]

    return MODULES.get(aaarg, None)


if __name__ == "__main__":
    try:
        selected_module = None

        if len(sys.argv) <= 1:
            logger.error(
                "Console mode is not supported, please run via `npm start` from root folder. See details in README.md."
            )
        else:
            selected_module = extract_from_args()
            if selected_module:
                selected_module.run()
            else:
                print("Invalid choice.")
    except KeyboardInterrupt:
        logger.info("Execution stopped.")
    except Exception as e:
        log_error(e)
        # raise e
