import sys

from dotenv import find_dotenv, load_dotenv
from modules.bridge.hyperlane.bridge_hyperlane import BridgeHyperlane
from modules.bridge.jumper.bridge_jumper import BridgeJumper
from modules.bridge.relay.bridge_relay import BridgeRelay
from modules.chore.rabby_import.rabby_import import RabbyImport
from modules.swap.jumper.swap_jumper import SwapJumper
from modules.swap.pancakeswap.swap_pancakeswap import SwapPancakeswap
from modules.testing.ads_execution.ads_execution import AdsExecution
from modules.transfer.transfer import Transfer
from modules.withdraw.okx.withdraw_okx import WithdrawOkx
from modules.yt_tokens.yt_tokens import YtTokens
from utils import (
    import_premium_module,
    log_error,
    logger,
    run_module,
    run_premium_module,
)

load_dotenv(find_dotenv("../.env"))

MODULES = {
    "withdraw-okx": WithdrawOkx,
    "bridge-jumper": BridgeJumper,
    "bridge-relay": BridgeRelay,
    "bridge-hyperlane": BridgeHyperlane,
    "swap-jumper": SwapJumper,
    "swap-pancakeswap": SwapPancakeswap,
    "transfer": Transfer,
    "yt_tokens": YtTokens,
    "chore-rabby_import": RabbyImport,
    "testing-ads_execution": AdsExecution,
}
PREMIUM_MODULES = {
    "premium/mint-kingdomly": import_premium_module("mint-kingdomly-mint_kingdomly", "MintKingdomly"),
    "premium/mint-magiceden": import_premium_module("mint-magiceden-mint_magiceden", "MintMagiceden"),
    "premium/farm-lighter": import_premium_module("farm-lighter-farm_lighter", "FarmLighter"),
    "premium/airdrop-perps": import_premium_module("airdrop-perps-airdrop_perps", "AirdropPerps"),
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
