import time
import re
import random

from multiprocessing import Pool
from utils import load_json, zip_to_addresses, sleep, log_error
from utils import logger

from modules.testnet.tools.ads import Ads
from modules.testnet.mitosis.helpers import (
    MITO_GAME_CELLS,
    DEPOSITS_ASSETS,
    CHROMO_MAIN_ASSET_TO_TRADE,
    CHROMO_ASSETS_TO_TRADE,
    TELO_ASSETS_TO_SUPPLY,
)


class TestnetMitosis:
    def __init__(
        self,
        profile,
        password,
        tasks,
        mito_game_time,
        chromo_swaps_count,
        supply_every_swap,
        initial_delay,
    ):
        sleep(initial_delay)
        self.profile = profile
        self.ads = Ads(profile, password)
        self.tasks = tasks
        self.mito_game_time = mito_game_time
        self.chromo_swaps_count = chromo_swaps_count
        self.supply_every_swap = supply_every_swap

    def mito_game(self):
        end_time = time.time() + self.mito_game_time * 60
        logger.info(f"Profile: {self.ads.profile_number} | Mito Game | Started for {self.mito_game_time} minute(s)")

        self.ads.open_url("https://testnet.mitosis.org/", '//button[@class="sc-14c346c2-0 jjElIw"]')
        sleep(1, 2)
        self.ads.click_element('//button[text()="Let\'s Play a Mini Game!"]')
        self.ads.rabby.sign()
        self.ads.while_present('//button[text()="Drawing lines..."]')
        sleep(5, 10)

        itterations = 0
        while time.time() < end_time:
            for cell_id in MITO_GAME_CELLS:
                try:
                    if self.ads.find_element(f'//div[@data-cell-id="{cell_id}"]', 1):
                        nested_element = self.ads.find_element(
                            f'//div[@data-cell-id="{cell_id}"]//div[@class="sc-e1a3e85d-8 itjPpa"]',
                            1,
                        )

                        if nested_element is not None and nested_element.get_attribute("innerHTML") != "":
                            self.ads.click_element(f'//div[@data-cell-id="{cell_id}"]', 1, True)
                except Exception:
                    continue

                sleep(0.1)

            itterations += 1

            if itterations % 7 == 0:
                remaining_time = max(1, end_time - time.time())
                logger.info(
                    f"Profile: {self.ads.profile_number} | Mito Game | {int(remaining_time // 60)} minute(s) and {int(remaining_time % 60)} second(s) left"
                )
            sleep(1)

        logger.success(f"Profile: {self.ads.profile_number} | Mito Game | Finished")

    def faucets(self):
        logger.info(f"Profile: {self.ads.profile_number} | Faceuts | Claim started")

        self.ads.open_url("https://testnet.mitosis.org/faucet", '//button[@class="sc-14c346c2-0 jjElIw"]')
        sleep(4, 5)
        self.ads.until_present('//h1[text()="Claim Your Free Testnet Tokens"]')

        self.ads.scroll("bottom")

        main_faceut = '(//div[@class="sc-3a941f41-0 jbOTHI"])[1]//button[text()="Claim Daily Tokens"]'
        if self.ads.find_element(main_faceut):
            self.ads.click_element(main_faceut)
            self.ads.while_present(main_faceut)
            sleep(2)
            logger.success(f"Profile: {self.ads.profile_number} | Faceuts | Claimed Main Faceut")
        else:
            logger.info(f"Profile: {self.ads.profile_number} | Faceuts | Main Faceut already claimed")

        bonus_faceut = '(//div[@class="sc-3a941f41-0 jbOTHI"])[2]//button[text()="Claim Daily Tokens"]'
        if self.ads.find_element(bonus_faceut):
            self.ads.click_element(bonus_faceut)
            self.ads.while_present(bonus_faceut)
            sleep(1, 2)
            logger.success(f"Profile: {self.ads.profile_number} | Faceuts | Claimed Bonus Faceut")
        else:
            logger.info(f"Profile: {self.ads.profile_number} | Faceuts | Bonus Faceut already claimed")

    def make_deposits(self):
        logger.info(f"Profile: {self.ads.profile_number} | Deposits | Depositing started")

        self.ads.open_url("https://testnet.mitosis.org/EOL-vault", '//button[@class="sc-14c346c2-0 jjElIw"]')
        sleep(4, 5)
        self.ads.click_element('//button[@class="sc-52d2482a-0 iIehYz"]')
        self.ads.until_present('//button[text()="Redeem"]')
        sleep(1, 2)

        for asset in DEPOSITS_ASSETS:
            sleep(3, 5)
            self.ads.click_element('//p[@class="sc-4ae4fd96-0 TAjxq"]')
            sleep(1, 2)
            self.ads.click_element(f'//button[p[text()="{asset["name"]}"]]')
            self.ads.until_present(f'//button[text()="Max"]//..//p[text()="{asset["name"]}"]')
            sleep(1, 2)

            for network in asset["networks"]:
                sleep(2, 3)
                self.ads.click_element(f'//button[div[p[text()="{network}"]]]')
                sleep(1, 2)

                balance_str = self.ads.find_element('//button[text()="Max"]/..').text.split("\n")[0]

                if balance_str == "< 0.0001" or float(balance_str) <= 0:
                    logger.info(
                        f"Profile: {self.ads.profile_number} | Deposits | Balance is 0 for {asset['name']} in {network}"
                    )
                    continue

                self.ads.click_element('//button[text()="Max"]')
                self.ads.until_present('(//button[text()="Deposit" and not(@disabled)])[2]')
                sleep(1, 2)
                self.ads.click_element('(//button[text()="Deposit" and not(@disabled)])[2]')
                sleep(1, 2)
                self.ads.rabby.sign()
                sleep(1, 2)
                self.ads.rabby.sign()
                sleep(1, 2)
                self.ads.until_present('//button[text()="Deposit" and @disabled]')
                logger.success(
                    f"Profile: {self.ads.profile_number} | Deposits | Deposited {balance_str} {asset['name']} from {network}"
                )

    def craft_cells(self):
        logger.info(f"Profile: {self.ads.profile_number} | Cells | Crafting started")

        self.ads.open_url("https://testnet.mitosis.org/mypage", '//button[@class="sc-14c346c2-0 jjElIw"]')
        sleep(4, 5)
        self.ads.while_present('//p[text()="Accumulated XP: " and strong[text()="0"]]')
        sleep(2, 3)

        if self.ads.find_element('//p[text()=" cells" and strong[text()="0" or text()="1"]]'):
            logger.info(f"Profile: {self.ads.profile_number} | Cells | No Cells to Craft")
            return

        self.ads.click_element('//button[text()="Craft"]')
        sleep(1, 2)

        timeout_duration = 60
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time > timeout_duration:
                logger.warning(f"Profile: {self.ads.profile_number} | Cells | Craft timeout")
                break

            cell_count = int(self.ads.find_element('//div[@class="sc-99846df6-3 omDtY"]').text.split("\n")[1])
            if cell_count <= 1:
                break

            self.ads.click_element('//button[text()="Synthesis" or text()="Synthesis Again"]')
            sleep(2.5, 3.5)

        self.ads.click_element('//button[@class="sc-52d2482a-0 caWALb sc-99846df6-2 cfTcwy"]')

        logger.success(f"Profile: {self.ads.profile_number} | Cells | Cells crafted")

    def make_swap(self, asset_from, asset_to):
        self.ads.click_element('//button[text()="100%"]')
        sleep(1, 2)
        self.ads.until_present(f'//button[text()="Swap" or text()="Approve [{asset_from}]"]')

        if self.ads.find_element(f'//button[text()="Approve [{asset_from}]"]'):
            self.ads.click_element(f'//button[text()="Approve [{asset_from}]"]')
            sleep(1, 2)
            self.ads.rabby.sign()
            sleep(1, 2)
            self.ads.while_present(f'//button[text()="Approving {asset_from}"]')
            sleep(1, 2)

        if self.ads.find_element('//button[text()="Swap"]'):
            retries = 0
            while retries < 5:
                self.ads.click_element('//button[text()="Swap"]')
                sleep(1, 2)
                self.ads.rabby.sign()
                sleep(1, 2)

                if self.ads.until_present('//div[span[text()="Swap successful"]]', 10):
                    sleep(1, 2)
                    swapped_from = self.ads.find_element(f'//span[contains(text(), " {asset_from}")]').text
                    swapped_to = self.ads.find_element(f'//span[contains(text(), " {asset_to}")]').text
                    self.ads.click_element('//div[@class="styles_buttonIcon__BR2iu styles_hasClick__62LM_"]')
                    logger.success(
                        f"Profile: {self.ads.profile_number} | Chromo | {asset_from}->{asset_to} | Swapped {swapped_from} -> {swapped_to}"
                    )
                    sleep(1, 2)
                    break
                else:
                    logger.warning(
                        f"Profile: {self.ads.profile_number} | Chromo | {asset_from}->{asset_to} | Retrying swap after failure"
                    )
                    retries += 1
                    sleep(3, 5)
                    self.ads.click_element('//button[text()="Close"]')
                    self.ads.click_element('//button[text()="100%"]')
                    self.ads.until_present(f'//button[text()="Swap" or text()="Approve [{asset_from}]"]')
                sleep(2)
            else:
                logger.error(
                    f"Profile: {self.ads.profile_number} | Chromo | {asset_from}->{asset_to} | Failed after {retries} retries"
                )

    def parse_balance(self, text):
        try:
            return float(re.search(r"[\d,]+\.\d+|[\d,]+", text).group().replace(",", ""))
        except Exception:
            return 0

    def swap_assets(self, asset_from, asset_to, swap_back=False):
        self.ads.open_url("https://app.chromo.exchange/swap")
        self.ads.until_present('//button[contains(text(), "0x")]')
        sleep(2, 3)

        # Select assets
        self.ads.click_element('//div[text()="Select token"]')
        sleep(1, 2)
        self.ads.input_text('//input[@placeholder="Search token"]', asset_from)
        sleep(1, 2)
        self.ads.click_element(f'//span[text()="{asset_from}"]')
        sleep(1, 2)
        self.ads.click_element('//div[text()="Select token"]')
        sleep(1, 2)
        self.ads.input_text('//input[@placeholder="Search token"]', asset_to)
        sleep(1, 2)
        self.ads.click_element(f'//div[span[text()="{asset_to}"]]')
        sleep(1, 2)

        # Make slippage higher
        self.ads.click_element('//div[span[text()="Setting"]]')
        sleep(1, 2)
        self.ads.click_element('//div[span[text()="Manual"]]')
        sleep(1, 2)
        self.ads.input_text('//input[@value="0.5"]', "3")
        sleep(1, 2)
        self.ads.click_element('//button[text()="Save"]')

        # Check balance
        balance_text = self.ads.find_element('//span[contains(text(), "Balance:")]').text
        balance = self.parse_balance(balance_text)

        if balance > 0:
            # Make swap
            self.make_swap(asset_from, asset_to)
            sleep(2, 3)
        else:
            logger.info(f"Profile: {self.ads.profile_number} | Chromo | {asset_from}->{asset_to} | Balance is 0")

        if not swap_back:
            sleep(2, 3)
            return

        sleep(2, 3)

        # Change Assets
        self.ads.click_element('//div[@class="styles_buttonIcon__BR2iu styles_hasClick__62LM_"]')

        tmp_asset = asset_from
        asset_from = asset_to
        asset_to = tmp_asset

        self.make_swap(asset_from, asset_to)
        sleep(3, 5)

    def telo_execute_action(self, asset, action, post_action, percentage):
        retries = 0
        while retries < 5:
            self.ads.click_element(f'//button[text()="{action}"]')
            sleep(1, 2)
            self.ads.until_present(f'//button[text()="{action} {asset}" and @disabled]')
            sleep(1, 2)

            balance_text = self.ads.find_element(f'//p[contains(text(), "Available to {action.lower()}:")]').text
            balance = self.parse_balance(balance_text)
            if balance <= 0:
                retries += 1
                self.ads.click_element('//button[span[text()="Close"]]')
                sleep(2, 3)
                continue

            self.ads.click_element(f'//span[text()="{percentage}%"]')
            sleep(1, 2)
            self.ads.click_element(f'//button[text()="{action} {asset}" and not(@disabled)]')
            sleep(1, 2)
            self.ads.rabby.sign()
            sleep(1, 2)
            self.ads.rabby.sign()
            sleep(1, 2)

            if self.ads.until_present(f'//p[text()="{post_action} successfully"]', 10):
                sleep(1, 2)
                self.ads.click_element('//button[text()="Confirm"]')
                logger.info(f"Profile: {self.ads.profile_number} | Telo | {asset} | {post_action} successfully")
                sleep(1, 2)
                break
            else:
                logger.warning(f"Profile: {self.ads.profile_number} | Telo | {asset} | Retrying {action} after failure")
                retries += 1
                sleep(1, 2)
                self.ads.click_element('//button[text()="Close"]')
                sleep(1, 2)
                self.ads.input_text('//input[@placeholder="Search for an asset"]', asset)
                sleep(1, 2)
            sleep(2, 3)
        else:
            logger.error(
                f"Profile: {self.ads.profile_number} | Telo | {asset} | {action} failed after {retries} retries"
            )

    def telo_suply_asset(self, asset, min_supply):
        logger.info(f"Profile: {self.ads.profile_number} | Telo | {asset} | Started")

        self.ads.open_url("https://app.telo.money/market")
        self.ads.while_present('//div[text()="No data found"]')
        sleep(2, 3)

        # Search
        self.ads.input_text('//input[@placeholder="Search for an asset"]', asset)
        sleep(5, 10)

        # Supply
        self.telo_execute_action(asset, "Supply", "Supplied", "80")
        sleep(30, 60)

        # Borrow
        self.telo_execute_action(asset, "Borrow", "Borrowed", "80")
        sleep(30, 60)

        # Repay
        self.telo_execute_action(asset, "Repay", "Repaid", "100")
        sleep(15, 30)
        self.telo_execute_action(asset, "Repay", "Repaid", "100")
        sleep(30, 60)

        # Withdraw
        self.telo_execute_action(asset, "Withdraw", "Withdrawn", "100")
        sleep(30, 60)

    def chromo_swaps(self):
        logger.info(
            f"Profile: {self.ads.profile_number} | Chromo | Chromo {self.chromo_swaps_count} auto-swaps and Telo supply every {self.supply_every_swap} swap started"
        )

        for asset in CHROMO_ASSETS_TO_TRADE:
            self.swap_assets(asset, CHROMO_MAIN_ASSET_TO_TRADE)

        for i in range(self.chromo_swaps_count // 2):
            i += 1
            swap_asset = random.choice(CHROMO_ASSETS_TO_TRADE)
            self.swap_assets(CHROMO_MAIN_ASSET_TO_TRADE, swap_asset, swap_back=True)
            logger.info(f"Profile: {self.ads.profile_number} | Chromo | {i * 2}/{self.chromo_swaps_count} done")

            if "mix_telo_supplies" in self.tasks and i % self.supply_every_swap == 0:
                supply_asset = random.choice(TELO_ASSETS_TO_SUPPLY)
                if supply_asset["symbol"] != CHROMO_MAIN_ASSET_TO_TRADE:
                    self.swap_assets(CHROMO_MAIN_ASSET_TO_TRADE, supply_asset["symbol"])

                self.telo_suply_asset(supply_asset["symbol"], supply_asset["min_supply"])

                if supply_asset["symbol"] != CHROMO_MAIN_ASSET_TO_TRADE:
                    self.swap_assets(supply_asset["symbol"], CHROMO_MAIN_ASSET_TO_TRADE)

            sleep(15, 30)

    def execute(self):
        try:
            logger.info(f"Profile: {self.ads.profile_number} | Tasks | {self.tasks}")

            self.ads.rabby.authenticate()

            sleep(15, 30)

            if "mito_game" in self.tasks:
                self.mito_game()
                sleep(15, 30)

            if "faceuts" in self.tasks:
                self.faucets()
                sleep(15, 30)

            if "make_deposits" in self.tasks:
                self.make_deposits()
                sleep(15, 30)

            if "craft_cells" in self.tasks:
                self.craft_cells()
                sleep(15, 30)

            if "chromo_swaps" in self.tasks:
                self.chromo_swaps()
                sleep(15, 30)

            self.ads.close_browser()
            return True
        except Exception as e:
            log_error(e, f"Profile: {self.profile}")

            return False

    @staticmethod
    def run_profile(profile, password, tasks, mito_game_time, chromo_swaps_count, supply_every_swap, initial_delay):
        TestnetMitosis(
            profile, password, tasks, mito_game_time, chromo_swaps_count, supply_every_swap, initial_delay
        ).execute()

    @classmethod
    def run(cls):
        instructions = load_json("modules/testnet/mitosis/instructions.json")

        profiles = instructions["profiles"]
        passwords = zip_to_addresses(profiles, instructions["passwords"])
        tasks = instructions["tasks"]
        mito_game_time = instructions["mito_game_time"]
        chromo_swaps_count = instructions["chromo_swaps_count"]
        supply_every_swap = instructions["supply_every_swap"]

        if instructions["parallel_execution"]:
            try:
                pool = Pool(processes=instructions["max_processes"])

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_profile,
                        args=(
                            profile,
                            passwords.get(profile, passwords[profiles[0]]),
                            tasks,
                            mito_game_time,
                            chromo_swaps_count,
                            supply_every_swap,
                            (i + 1) * 5,
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
                    passwords.get(profile, passwords[profiles[0]]),
                    tasks,
                    mito_game_time,
                    chromo_swaps_count,
                    supply_every_swap,
                    (i + 1) * 5,
                ).execute()