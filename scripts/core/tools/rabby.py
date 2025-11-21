import os

from selenium.common import NoSuchWindowException
from utils import ExecutionError, logger, sleep


class Rabby:
    IDENTIFIER = "acmacodkjbdgmoleebolmdjonilkdbch"
    UNLOCK_PATH = "unlock"

    def __init__(self, ads, password):
        self.ads = ads
        self.password = password
        self.identifier = os.getenv("RABY_IDENTIFIER", self.IDENTIFIER)
        self.unlock_path = os.getenv("RABY_UNLOCK_PATH", self.UNLOCK_PATH)
        self._is_authenticated = False

    def url(self):
        return f"chrome-extension://{self.identifier}/index.html"

    def unlock_url(self):
        return f"chrome-extension://{self.identifier}/index.html#/{self.unlock_path}"

    def open(self):
        self.ads.open_url(self.url())

    def authenticate(self) -> None:
        if not self._is_authenticated:
            self.ads.open_url(self.url())

            if self.ads.find_element('//div[text()="Swap"]', 2):
                logger.info(f"Profile: {self.ads.label} | Rabby | Already authenticated")
                self._is_authenticated = True
            else:
                self.ads.open_url(self.unlock_url())

                self.ads.input_text('//input[@placeholder="Enter the Password to Unlock"]', self.password)
                self.ads.click_element('//button[span[text()="Unlock"]]')
                if not self.ads.until_present('//div[text()="Swap"]', 15):
                    raise ExecutionError("Rabby auth failed")

                self._is_authenticated = True
                logger.success(f"Profile: {self.ads.label} | Rabby | Authenticated")

            self.ads.new_tab()
            self.ads.close_all_other_tabs()

    def sign(self):
        logger.debug(f"Profile: {self.ads.label} | Rabby | Signing transaction")
        current_tab = self.ads.current_tab()
        signed = False

        for _ in range(5):
            target_tab = self.ads.find_tab("notification.html", keep_focused=True)
            if target_tab:
                if not self.ads.click_element('//button[span[contains(text(), "Sign")] and not(@disabled)]', 10):
                    logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to sign")
                    break
                sleep(0.5, 1)
                try:
                    self.ads.click_element('//button[text()="Confirm"]')
                    if not self.ads.until_present('//span[text()="Transaction created"]', 25):
                        if self.ads.find_element('//span[text()="Fail to create"]'):
                            self.ads.click_element('//button[span[text()="Cancel"]]')
                            logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to create")
                            break
                except NoSuchWindowException:
                    pass
                signed = True
                break
            sleep(1)

        self.ads.switch_tab(current_tab)

        return signed

    def fast_sign(self):
        logger.debug(f"Profile: {self.ads.label} | Rabby | Fast Signing transaction")
        current_tab = self.ads.current_tab()
        signed = False

        for _ in range(25000):
            target_tab = self.ads.find_tab("notification.html", keep_focused=True)
            if target_tab:
                logger.info(f"Profile: {self.ads.label} | Rabby | Trying to sign")
                self.ads.hover_element('//span[text()="Normal"] | //span[text()="Fast"] | //span[text()="Instant"]', 25)
                self.ads.click_element('//div[text()="Instant"]', 25)
                if self.ads.find_element('//button[span[text()="Sign and Create"]]', 25).get_attribute("disabled"):
                    if self.ads.find_element('//span[text()="Please process the alert before signing"]', 1):
                        self.ads.click_element('//span[text()="Ignore all"]', 1)

                self.ads.click_element('//button[span[text()="Sign and Create"] and not(@disabled)]', 25)
                self.ads.click_element('//button[text()="Confirm" and not(@disabled)]', 25)
                try:
                    self.ads.until_present('//span[text()="Transaction created"]', 25)
                except NoSuchWindowException:
                    pass
                logger.success(f"Profile: {self.ads.label} | Rabby | Transaction signed")
                signed = True
                break
            self.ads.switch_tab(current_tab)
            sleep(0.1, 0.2)

        return signed

    def connect(self):
        logger.debug(f"Profile: {self.ads.label} | Rabby | Connecting")
        current_tab = self.ads.current_tab()
        connected = False

        for _ in range(1):
            target_tab = self.ads.find_tab("notification.html#/approval", keep_focused=True)
            if target_tab:
                if not self.ads.click_element('//button[span[text()="Connect"]]', 10):
                    logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to sign")
                    break
                sleep(0.5, 1)
                connected = True
                break
            sleep(1)

        self.ads.switch_tab(current_tab)

        return connected

    def import_new(self, label, address, password, private_key):
        self.ads.open_url(self.url())
        sleep(1, 2)

        self.ads.click_element('//button[span[text()="Next"]]', 1)
        self.ads.click_element('//button[span[text()="Get Started"]]', 1)

        self.ads.click_element('//div[text()="Import Private Key"]', 1)
        self.ads.click_element('//button[span[text()="Get Started"]]', 1)

        self.ads.click_element('//div[text()="Import Private Key"]', 1)
        self.ads.input_text('//input[@placeholder="Password must be at least 8 characters long"]', password)
        self.ads.input_text('//input[@placeholder="Confirm password"]', password)
        self.ads.click_element('//button[span[text()="Next"]]')

        self.ads.input_text('//input[@placeholder="Enter your Private key"]', private_key)
        self.ads.click_element('//button[span[text()="Confirm"]]')

        import_address = self.ads.find_element('//div[@class="address-viewer-text subtitle"]').text

        if import_address.lower() != address.lower():
            raise ExecutionError("Address is not matching the one uner private key.")

        self.ads.open_url(self.url())
        self.ads.click_element('//button[@class="ant-modal-close"]', 2)
        self.ads.click_element('//div[@class="current-address"]', 1)
        self.ads.click_element('//div[@class="rabby-address-item-title"]', 1)
        self.ads.click_element('//div[text()="Address Note"]//..//img', 1)
        sleep(1, 2)
        self.ads.click_element('//span[@class="anticon anticon-close-circle ant-input-clear-icon"]')
        self.ads.input_text('//input[@placeholder="Please input address note"]', label)
        self.ads.click_element('//button[span[text()="Confirm"]]')
