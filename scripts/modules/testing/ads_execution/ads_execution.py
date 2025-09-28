import asyncio
import os
import signal
import sys
from multiprocessing import Pool

try:
    from utils import sleep
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
    try:
        from utils import sleep
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))
        from utils import sleep

from core.helpers import zip_to_objects
from core.tools.ads import Ads
from utils import load_json, logger, sleep


class AdsExecution:
    def __init__(self, profile, label, password, process=None):
        self.profile = profile
        self.label = label
        self.label = password
        self.process = process
        self.ads = Ads(profile, wallet_password=password, label=label)

    def log_prefix(self):
        if self.process:
            return f"P{self.process} | "
        else:
            return ""

    async def stop(self):
        logger.info(f"{self.log_prefix()}Stopping trading strategy")
        await self.ads.close_browser()

    async def start(self):
        await self.ads.start()
        logger.info(f"{self.log_prefix()}Starting trading strategy")
        await self.ads.wallet.authenticate()
        logger.info("Openning lighter...")
        await self.ads.open_url("https://app.lighter.xyz/trade/ETH", sleep_time=2)
        if not await self.ads.until_present('//button[contains(text(), "Positions")]', 30):
            logger.error(f"{self.log_prefix()} Test passed unsuccessfully")
        else:
            logger.success(f"{self.log_prefix()} Test passed successfully")
        await self.ads.close_browser()

    @classmethod
    def run_batch(cls, profile, labels, passwords, process=None):
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

        instance = None
        try:
            instance = cls(profile=profile, label=labels[profile], password=passwords[profile], process=process)

            asyncio.run(instance.start())
        except (KeyboardInterrupt, SystemExit):
            asyncio.run(instance.stop())
            raise

    @classmethod
    def run(cls):
        instructions = load_json("modules/testing/ads_execution/instructions.json")
        profiles = instructions["profiles"]
        labels = zip_to_objects(profiles, instructions["labels"])
        passwords = zip_to_objects(profiles, instructions["passwords"])

        if instructions["parallel_execution"]:
            pool = None
            try:
                pool = Pool(processes=len(profiles))

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_batch,
                        args=(profile, labels, passwords, i + 1),
                    )

                pool.close()
                pool.join()

            except KeyboardInterrupt:
                logger.info("Received KeyboardInterrupt, terminating all processes...")
                if pool:
                    pool.terminate()
                    pool.join()
                logger.info("All parallel processes are terminated.")
                raise
        else:
            try:
                for i, profile in enumerate(profiles):
                    cls.run_batch(profile, labels, passwords)
            except KeyboardInterrupt:
                logger.info("Single process execution interrupted.")
                raise
