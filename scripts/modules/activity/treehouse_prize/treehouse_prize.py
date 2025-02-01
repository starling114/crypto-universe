import json
import time
from datetime import datetime, timedelta
import requests
from multiprocessing import Pool
from utils import load_json, sleep, log_error
from utils import logger

from core.tools.ads import Ads


class TreehousePrize:
    def __init__(self, profile, password, prize_time):
        self.profile = profile
        self.ads = Ads(profile, password)
        self.password = password
        self.prize_time = prize_time

    def execute(self):
        try:
            logger.info(f"Profile: {self.ads.profile} | Treehouse Prize | Starting")

            self.ads.wallet.authenticate()
            sleep(1, 2)

            self.ads.open_url("https://app.treehouse.finance/portfolio")
            sleep(1)

            self.ads.click_element(
                '//button[@class="p-[1.5px] ml-auto cursor-pointer flex-shrink-0 w-[19px] h-[19px] outline-none"]', 2
            )
            sleep(1, 2)
            self.ads.click_element(
                '//button[@class="p-[1.5px] ml-auto cursor-pointer flex-shrink-0 w-[19px] h-[19px]"]', 2
            )
            sleep(1, 2)

            if not self.ads.click_element('//button[span[text()="Connect Wallet"]]', 1):
                self.ads.open_url("https://app.treehouse.finance/portfolio")
                sleep(3, 5)

            if self.ads.click_element('//button[span[text()="Connect Wallet"]]', 1):
                sleep(1, 2)
                self.ads.scroll(
                    "bottom",
                    xpath='//div[@class="text-grey-0 max-h-[224px] md:max-h-[108px] overflow-auto text-md leading-[1.1875em] space-y-4"]',
                )
                self.ads.click_element('//button[text()="I Confirm"]')
                sleep(1, 2)

                self.ads.click_element('//h2[text()="Connect Wallet"]//..//..//button[@role="checkbox"]')
                sleep(1, 2)

                self.ads.click_element('//h3[text()="Rabby Wallet"]')
                sleep(1, 2)

                self.ads.wallet.connect()
                sleep(1, 2)

            logger.info(f"Profile: {self.ads.profile} | Treehouse Prize | Connected")

            self.ads.scroll("bottom")
            sleep(1, 2)

            self.ads.click_element('//img[@src="/cny-assets/cny-badge-enabled.svg"]')
            sleep(1, 2)

            hour, minute, second = list(map(int, self.prize_time.split(":")))
            now = datetime.now()

            target_datetime = datetime(now.year, now.month, now.day, hour, minute, second)
            target_timestamp = target_datetime.timestamp()

            cycles = 0
            while time.time() < target_timestamp:
                cycles += 1
                if cycles % 10 == 0:
                    logger.info(
                        f"Profile: {self.ads.profile} | Treehouse Prize | Cycle #{cycles} waiting for {target_datetime}"
                    )
                sleep(1, 5)

            logger.info(f"Profile: {self.ads.profile} | Treehouse Prize | Starting claim")

            tokens = self.ads.execute_script(
                """
                    return Object.keys(localStorage)
                        .filter(key => key.startsWith('token-'))
                        .map(key => ({ [key]: localStorage.getItem(key) }));
                """
            )
            parsed_data = json.loads(list(tokens[0].values())[0])
            address = parsed_data.get("address")
            access_token = parsed_data.get("access_token")
            if not address or not access_token:
                logger.error(f"Profile: {self.ads.profile} | Treehouse Prize | Access not extracted from local store")
                return False

            target_claim_timestamp = (target_datetime + timedelta(minutes=30)).timestamp()
            cycles = 0
            while time.time() < target_claim_timestamp:
                try:
                    cycles += 1
                    response = requests.get(
                        f"https://api.treehouse.finance/campaign/claim?address=${address}",
                        headers={
                            "accept": "*/*",
                            "accept-language": "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6,pl;q=0.5,pt-BR;q=0.4,pt;q=0.3",
                            "content-type": "application/json",
                            "priority": "u=1, i",
                            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": '"macOS"',
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-site",
                            "session-key": access_token,
                            "Referer": "https://app.treehouse.finance/",
                            "Referrer-Policy": "strict-origin-when-cross-origin",
                        },
                    )
                    response_json = response.json()
                    if response_json.get("message", None) == "already claimed today":
                        logger.warning(f"Profile: {self.ads.profile} | Treehouse Prize | Already claimed")
                        break
                    logger.info(f"Profile: {self.ads.profile} | Treehouse Prize | Response: ${response_json}")
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    logger.error(
                        f"Profile: {self.ads.profile} | Error: {e} | Cycle #{cycles}. Retrying until {target_claim_timestamp}"
                    )
                    sleep(1, 2)

            logger.success(f"Profile: {self.ads.profile} | Treehouse Prize | Claimed Successfully")
            self.ads.close_browser()
            return True
        except Exception as e:
            log_error(e, f"Profile: {self.profile}")

            return False

    @staticmethod
    def run_profile(profile, password, prize_time, initial_delay):
        try:
            sleep(initial_delay)
            TreehousePrize(profile, password, prize_time).execute()
        except Exception as e:
            log_error(e, f"Profile: {profile}")

    @classmethod
    def run(cls):
        instructions = load_json("modules/activity/treehouse_prize/instructions.json")

        profiles = instructions["profiles"]

        if instructions["parallel_execution"]:
            try:
                pool = Pool(processes=instructions["max_processes"])

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_profile,
                        args=(
                            profile,
                            instructions["password"],
                            instructions["prize_time"],
                            (i % instructions["max_processes"]) * 1,
                        ),
                    )

                pool.close()
                pool.join()
            except KeyboardInterrupt as e:
                pool.terminate()
                pool.join()
                logger.info("All parallel processes are terminated.")
                raise e
        else:
            for i, profile in enumerate(profiles):
                cls(
                    profile,
                    instructions["password"],
                    instructions["prize_time"],
                    (i + 1) * 5,
                ).execute()
