import sys
from dotenv import load_dotenv, find_dotenv

from modules.withdraw.okx.withdraw_okx import WithdrawOkx
from modules.bridge.jumper.bridge_jumper import BridgeJumper
from modules.bridge.relay.bridge_relay import BridgeRelay
from modules.bridge.hyperlane.bridge_hyperlane import BridgeHyperlane
from modules.swap.jumper.swap_jumper import SwapJumper
from modules.transfer.transfer import Transfer
from modules.yt_tokens.yt_tokens import YtTokens
from modules.testnet.mitosis.testnet_mitosis import TestnetMitosis
from modules.activity.treehouse_prize.treehouse_prize import TreehousePrize
from modules.chore.rabby_import.rabby_import import RabbyImport

from utils import log_error, logger, import_premium_module, run_module, run_premium_module

load_dotenv(find_dotenv("../.env"))

MODULES = {
    "withdraw-okx": WithdrawOkx,
    "bridge-jumper": BridgeJumper,
    "bridge-relay": BridgeRelay,
    "bridge-hyperlane": BridgeHyperlane,
    "swap-jumper": SwapJumper,
    "transfer": Transfer,
    "yt_tokens": YtTokens,
    "testnet-mitosis": TestnetMitosis,
    "activity-treehouse_prize": TreehousePrize,
    "chore-rabby_import": RabbyImport,
}
PREMIUM_MODULES = {
    "premium/sale-fjord": import_premium_module("sale-fjord-sale_fjord", "SaleFjord"),
    "premium/mint-kingdomly": import_premium_module("mint-kingdomly-mint_kingdomly", "MintKingdomly"),
    "premium/mint-magiceden": import_premium_module("mint-magiceden-mint_magiceden", "MintMagiceden"),
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
