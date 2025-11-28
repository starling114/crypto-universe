import os

from utils import ExecutionError, logger, sleep


class Rabby:
    IDENTIFIER = "acmacodkjbdgmoleebolmdjonilkdbch"
    UNLOCK_PATH = "unlock"

    def __init__(self, browser, password):
        self.browser = browser
        self.password = password
        self.identifier = os.getenv("RABY_IDENTIFIER", self.IDENTIFIER)
        self.unlock_path = os.getenv("RABY_UNLOCK_PATH", self.UNLOCK_PATH)
        self._is_authenticated = False

    def url(self):
        return f"chrome-extension://{self.identifier}/index.html"

    def unlock_url(self):
        return f"chrome-extension://{self.identifier}/index.html#/{self.unlock_path}"

    def authenticate(self) -> None:
        if not self._is_authenticated:
            self.browser.open_url(self.url())

            if self.browser.find_element("//div[text()='Swap']", 2):
                logger.info(f"Profile: {self.browser.label} | Rabby | Already authenticated")
                self._is_authenticated = True
            else:
                self.browser.open_url(self.unlock_url())

                self.browser.input_text("//input[@placeholder='Enter the Password to Unlock']", self.password)
                self.browser.click_element("//button[span[text()='Unlock']]")
                if not self.browser.until_present("//div[text()='Swap']", 15):
                    raise ExecutionError("Rabby auth failed")

                self._is_authenticated = True
                logger.success(f"Profile: {self.browser.label} | Rabby | Authenticated")

            self.browser.new_tab()
            self.browser.close_other_tabs()

    def sign(self):
        logger.debug(f"Profile: {self.browser.label} | Rabby | Signing transaction")
        result = False

        main_page = self.browser.page
        popup_page = self.browser.context.wait_for_event("page", timeout=3000)
        self.browser.switch_tab(popup_page)
        if popup_page:
            if not self.browser.click_element(
                "//button[span[contains(text(), 'Sign')] and not(@disabled)]", timeout=10
            ):
                logger.warning(f"Profile: {self.browser.label} | Rabby | Failed to sign")
                result = False
            else:
                sleep(0.5, 1)
                self.browser.click_element("//button[text()='Confirm']")
                if not self.browser.until_present("//span[text()='Transaction created']", 25):
                    if self.browser.find_element("//span[text()='Fail to create']"):
                        self.browser.click_element("//button[span[text()='Cancel']]")
                        logger.warning(f"Profile: {self.browser.label} | Rabby | Failed to create")
                        result = False
                    else:
                        result = True
                else:
                    result = True
        self.browser.switch_tab(main_page)
        sleep(1)

        return result

    def connect(self):
        logger.debug(f"Profile: {self.browser.label} | Rabby | Connecting")
        result = False

        main_page = self.browser.page
        popup_page = self.browser.context.wait_for_event("page", timeout=3000)
        self.browser.switch_tab(popup_page)
        if popup_page:
            if not self.browser.click_element("//button[span[text()='Connect']]"):
                logger.warning(f"Profile: {self.browser.label} | Rabby | Failed to sign")
                result = False
            else:
                result = True
        self.browser.switch_tab(main_page)
        sleep(1)

        return result

    def import_new(self, label, address, password, private_key):
        self.browser.open_url(self.url())
        sleep(1, 2)

        self.browser.click_element('//button[span[text()="Next"]]', 1)
        self.browser.click_element('//button[span[text()="Get Started"]]', 1)

        self.browser.click_element('//div[text()="Import Private Key"]', 1)
        self.browser.click_element('//button[span[text()="Get Started"]]', 1)

        self.browser.click_element('//div[text()="Import Private Key"]', 1)
        self.browser.input_text('//input[@placeholder="Password must be at least 8 characters long"]', password)
        self.browser.input_text('//input[@placeholder="Confirm password"]', password)
        self.browser.click_element('//button[span[text()="Next"]]')

        self.browser.input_text('//input[@placeholder="Enter your Private key"]', private_key)
        self.browser.click_element('//button[span[text()="Confirm"]]')

        import_address = self.browser.element_text('//div[@class="address-viewer-text subtitle"]')

        if import_address.lower() != address.lower():
            raise ExecutionError("Address is not matching the one uner private key.")

        self.browser.open_url(self.url())
        self.browser.click_element('//button[@class="ant-modal-close"]', 2)
        self.browser.click_element('//div[@class="current-address"]', 1)
        self.browser.click_element('//div[@class="rabby-address-item-title"]', 1)
        self.browser.click_element('//div[text()="Address Note"]//..//img', 1)
        sleep(1, 2)
        self.browser.click_element('//span[@class="anticon anticon-close-circle ant-input-clear-icon"]')
        self.browser.input_text('//input[@placeholder="Please input address note"]', label)
        self.browser.click_element('//button[span[text()="Confirm"]]')
