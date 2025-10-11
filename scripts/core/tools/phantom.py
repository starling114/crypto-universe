import os

from selenium.common import NoSuchWindowException
from utils import ExecutionError, logger, sleep


class Phantom:
    IDENTIFIER = "bfnaelmomeimhlpmgjnjophhpkkoljpa"

    def __init__(self, ads, password):
        self.ads = ads
        self.password = password
        self.identifier = self.IDENTIFIER
        self._is_authenticated = False

    def url(self):
        return f"chrome-extension://{self.identifier}/popup.html"

    def open(self):
        self.ads.open_url(self.url())

    def authenticate(self) -> None:
        if not self._is_authenticated:
            self.ads.open_url(self.url())

            if self.ads.find_element('//div[text()="Receive"]', 2):
                logger.info(f"Profile: {self.ads.label} | Phantom | Already authenticated")
                self._is_authenticated = True
                return

            self.ads.input_text('//input[@data-testid="unlock-form-password-input"]', self.password)
            self.ads.click_element('//button[@data-testid="unlock-form-submit-button"]')
            if not self.ads.until_present('//div[text()="Receive"]', 15):
                raise ExecutionError("Phantom auth failed")

            self._is_authenticated = True
            logger.success(f"Profile: {self.ads.label} | Phantom | Authenticated")

    # def sign(self):
    #     logger.debug(f"Profile: {self.ads.label} | Phantom | Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False

    #     for _ in range(5):
    #         target_tab = self.ads.find_tab("notification.html", keep_focused=True)
    #         if target_tab:
    #             if not self.ads.click_element('//button[span[contains(text(), "Sign")] and not(@disabled)]', 10):
    #                 logger.warning(f"Profile: {self.ads.label} | Phantom | Failed to sign")
    #                 break
    #             sleep(0.5, 1)
    #             try:
    #                 self.ads.click_element('//button[text()="Confirm"]')
    #                 if not self.ads.until_present('//span[text()="Transaction created"]', 25):
    #                     if self.ads.find_element('//span[text()="Fail to create"]'):
    #                         self.ads.click_element('//button[span[text()="Cancel"]]')
    #                         logger.warning(f"Profile: {self.ads.label} | Phantom | Failed to create")
    #                         break
    #             except NoSuchWindowException:
    #                 pass
    #             signed = True
    #             break
    #         sleep(1)

    #     self.ads.switch_tab(current_tab)

    #     return signed

    # def fast_sign(self):
    #     logger.debug(f"Profile: {self.ads.label} | Phantom | Fast Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False

    #     for _ in range(25000):
    #         target_tab = self.ads.find_tab("notification.html", keep_focused=True)
    #         if target_tab:
    #             logger.info(f"Profile: {self.ads.label} | Phantom | Trying to sign")
    #             self.ads.hover_element('//span[text()="Normal"] | //span[text()="Fast"] | //span[text()="Instant"]', 25)
    #             self.ads.click_element('//div[text()="Instant"]', 25)
    #             if self.ads.find_element('//button[span[text()="Sign and Create"]]', 25).get_attribute("disabled"):
    #                 if self.ads.find_element('//span[text()="Please process the alert before signing"]', 1):
    #                     self.ads.click_element('//span[text()="Ignore all"]', 1)

    #             self.ads.click_element('//button[span[text()="Sign and Create"] and not(@disabled)]', 25)
    #             self.ads.click_element('//button[text()="Confirm" and not(@disabled)]', 25)
    #             try:
    #                 self.ads.until_present('//span[text()="Transaction created"]', 25)
    #             except NoSuchWindowException:
    #                 pass
    #             logger.success(f"Profile: {self.ads.label} | Phantom | Transaction signed")
    #             signed = True
    #             break
    #         self.ads.switch_tab(current_tab)
    #         sleep(0.1, 0.2)

    #     return signed

    # def connect(self):
    #     logger.debug(f"Profile: {self.ads.label} | Phantom | Connecting")
    #     current_tab = self.ads.current_tab()
    #     connected = False

    #     for _ in range(1):
    #         target_tab = self.ads.find_tab("notification.html#/approval", keep_focused=True)
    #         if target_tab:
    #             if not self.ads.click_element('//button[span[text()="Connect"]]', 10):
    #                 logger.warning(f"Profile: {self.ads.label} | Phantom | Failed to sign")
    #                 break
    #             sleep(0.5, 1)
    #             connected = True
    #             break
    #         sleep(1)

    #     self.ads.switch_tab(current_tab)

    #     return connected

    def import_new(self, label, address, password, recovery_phrase):
        self.ads.open_url(f"chrome-extension://{self.identifier}/onboarding.html")
        sleep(1, 2)

        self.ads.click_element('//button[text()="I already have a wallet"]')
        self.ads.click_element('//div[text()="Import Recovery Phrase"]')

        for i, word in enumerate(recovery_phrase.split(" ")):
            self.ads.input_text(f"//input[@data-testid='secret-recovery-phrase-word-input-{i}']", word, single=True)

        self.ads.click_element('//button[text()="Import Wallet"]')
        self.ads.click_element('//button[text()="Continue"]')

        self.ads.input_text('//input[@data-testid="onboarding-form-password-input"]', password, single=True)
        self.ads.input_text('//input[@data-testid="onboarding-form-confirm-password-input"]', password, single=True)
        self.ads.click_element('//span[@data-state="unchecked"]')
        self.ads.click_element('//button[text()="Continue"]')

        self.ads.until_present('//button[text()="Continue"]')

        self.ads.open_url(self.url())
        self.ads.click_element('//button[@data-testid="settings-menu-open-button"]', sleep_time=0.3)
        sleep(2)
        self.ads.click_element('//button[@data-testid="sidebar_menu-button-settings"]', sleep_time=0.3)
        sleep(2)
        self.ads.click_element('//div[text()="Manage Accounts"]', sleep_time=0.3)
        sleep(2)
        self.ads.click_element('//p[text()="Account 1"]', sleep_time=0.3)
        self.ads.click_element('//p[text()="Account 1"]', sleep_time=0.3)
        self.ads.click_element('//div[text()="Account Name"]', sleep_time=0.3)

        self.ads.input_text('//input[@name="name"]', label, single=True)
        self.ads.click_element('//button[text()="Save"]', sleep_time=0.3)
