from utils import logger, sleep
from selenium.common import NoSuchWindowException


class Rabby:
    URL = "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/popup.html"

    def __init__(self, ads, password):
        self.ads = ads
        self.password = password

    def open(self):
        self.ads.open_url(Rabby.URL)

    def authenticate(self) -> None:
        self.open()

        if not self.ads.find_element('//button[span[text()="Unlock"]]', 2):
            logger.info(f"Profile: {self.ads.profile} | Rabby | Already authenticated")
            return

        self.ads.input_text('//input[@placeholder="Enter the Password to Unlock"]', self.password)
        self.ads.click_element('//button[span[text()="Unlock"]]')
        if not self.ads.find_element('//div[@class="gasprice"]', 15):
            raise Exception("Rabby auth failed")
        logger.success(f"Profile: {self.ads.profile} | Rabby | Authenticated")

    def connect(self):
        logger.debug(f"Profile: {self.ads.profile} | Rabby | Connecting")
        current_tab = self.ads.current_tab()
        connected = False
        sleep(3, 5)

        for _ in range(1):
            target_tab = self.ads.find_tab("notification.html#/approval", keep_focused=True)
            if target_tab:
                sleep(2, 3)
                if not self.ads.click_element('//button[span[text()="Connect"]]', 10):
                    logger.warning(f"Profile: {self.ads.profile} | Rabby | Failed to sign")
                    break
                sleep(0.5, 1)
                connected = True
            sleep(1, 2)

        self.ads.switch_tab(current_tab)
        sleep(2, 3)

        return connected

    def sign(self):
        logger.debug(f"Profile: {self.ads.profile} | Rabby | Signing transaction")
        current_tab = self.ads.current_tab()
        signed = False
        sleep(2.5, 3.5)

        for _ in range(5):
            target_tab = self.ads.find_tab("notification.html", keep_focused=True)
            if target_tab:
                sleep(2, 3)
                if not self.ads.click_element('//button[span[text()="Sign and Create"] and not(@disabled)]', 10):
                    logger.warning(f"Profile: {self.ads.profile} | Rabby | Failed to sign")
                    break
                sleep(0.5, 1)
                self.ads.click_element('//button[text()="Confirm"]')
                sleep(1, 2)
                try:
                    if not self.ads.until_present('//span[text()="Transaction created"]', 25):
                        if self.ads.find_element('//span[text()="Fail to create"]'):
                            self.ads.click_element('//button[span[text()="Cancel"]]')
                            logger.warning(f"Profile: {self.ads.profile} | Rabby | Failed to create")
                            break
                except NoSuchWindowException:
                    pass
                signed = True
            sleep(1, 2)

        self.ads.switch_tab(current_tab)
        sleep(2, 3)

        return signed

    def fast_sign(self):
        logger.debug(f"Profile: {self.ads.profile} | Rabby | Fast Signing transaction")
        current_tab = self.ads.current_tab()
        signed = False

        for _ in range(25000):
            target_tab = self.ads.find_tab("notification.html", keep_focused=True)
            if target_tab:
                logger.info(f"Profile: {self.ads.profile} | Rabby | Trying to sign")
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
                logger.success(f"Profile: {self.ads.profile} | Rabby | Transaction signed")
                signed = True
                break
            self.ads.switch_tab(current_tab)
            sleep(0.1, 0.2)

        return signed
