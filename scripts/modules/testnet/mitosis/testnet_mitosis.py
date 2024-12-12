import time

from multiprocessing import Pool
from utils import load_json, zip_to_addresses, sleep, log_error
from utils import logger

from modules.testnet.tools.ads import Ads
from modules.testnet.mitosis.helpers import *


class TestnetMitosis:
    def __init__(
        self,
        profile,
        password,
        tasks,
        initial_delay,
    ):
        sleep(initial_delay)
        self.profile = profile
        self.ads = Ads(profile, password)
        self.tasks = tasks

    def mito_game(self):
        end_time = time.time() + MITO_PLAY_MINUTES * 60
        logger.info(f"Profile: {self.ads.profile_number} | Mito Game | Started for {MITO_PLAY_MINUTES} minute(s)")

        self.ads.open_url("https://testnet.mitosis.org/", '//button[@class="sc-14c346c2-0 jjElIw"]')
        sleep(1, 2)
        self.ads.click_element('//button[text()="Let\'s Play a Mini Game!"]')
        self.ads.rabby.sign()
        self.ads.while_present('//button[text()="Drawing lines..."]')

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
                            self.ads.click_element(f'//div[@data-cell-id="{cell_id}"]', 1)
                except Exception:
                    pass

                sleep(0.1)

            itterations += 1

            if itterations % 7 == 0:
                remaining_time = max(1, end_time - time.time())
                logger.info(
                    f"Profile: {self.ads.profile_number} | Mito Game | {int(remaining_time // 60)} minute(s) and {int(remaining_time % 60)} second(s) left"
                )
            sleep(1)

        logger.success(f"Profile: {self.ads.profile_number} | Mito Game | Finished")
        sleep(3, 5)

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

        sleep(3, 5)

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

                balance_srt = self.ads.find_element('//button[text()="Max"]/..').text.split("\n")[0]
                if balance_srt == "< 0.0001" or float(balance_srt) <= 0:
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
                    f"Profile: {self.ads.profile_number} | Deposits | Deposited {balance_srt} {asset['name']} from {network}"
                )

        sleep(3, 5)

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
                logger.error(f"Profile: {self.ads.profile_number} | Cells | Craft timeout")
                break

            cell_count = int(self.ads.find_element('//div[@class="sc-99846df6-3 omDtY"]').text.split("\n")[1])
            if cell_count <= 1:
                break

            self.ads.click_element('//button[text()="Synthesis" or text()="Synthesis Again"]')
            sleep(2.5, 3.5)

        self.ads.click_element('//button[@class="sc-52d2482a-0 caWALb sc-99846df6-2 cfTcwy"]')

        logger.sucess(f"Profile: {self.ads.profile_number} | Cells | Cells crafted")

    def execute(self):
        try:
            logger.info(f"Profile: {self.ads.profile_number} | Tasks | {self.tasks}")

            self.ads.rabby.authenticate()

            if "mito_game" in self.tasks:
                self.mito_game()

            if "faceuts" in self.tasks:
                self.faucets()

            if "make_deposits" in self.tasks:
                self.make_deposits()

            if "craft_cells" in self.tasks:
                self.craft_cells()

            self.ads.close_browser()
            return True
        except Exception as e:
            log_error(e, f"Profile: {self.profile}")

            return False

    @staticmethod
    def run_profile(profile, password, tasks, initial_delay):
        try:
            TestnetMitosis(profile, password, tasks, initial_delay).execute()
        except Exception as e:
            log_error(e, f"Profile: {profile}")

    @classmethod
    def run(cls):
        instructions = load_json("modules/testnet/mitosis/instructions.json")

        profiles = instructions["profiles"]
        passwords = zip_to_addresses(profiles, instructions["passwords"])
        tasks = instructions["tasks"]

        if instructions["parallel_execution"]:
            try:
                pool = Pool(processes=instructions["max_processes"])

                for i, profile in enumerate(profiles):
                    pool.apply_async(
                        cls.run_profile, args=(profile, passwords.get(profile, passwords[profiles[0]]), tasks, i * 2)
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
                cls(profile, passwords[profile], tasks, i * 2).execute()
