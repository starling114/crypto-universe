import os

from utils import ExecutionError, logger


class Rabby:
    IDENTIFIER = "acmacodkjbdgmoleebolmdjonilkdbch"
    UNLOCK_PATH = "unlock"

    def __init__(self, ads, password):
        self.ads = ads
        self.password = password
        self.identifier = os.getenv("RABY_IDENTIFIER", self.IDENTIFIER)
        self.unlock_path = os.getenv("RABY_UNLOCK_PATH", self.UNLOCK_PATH)
        self.unlock_url = f"chrome-extension://{self.identifier}/index.html#/{self.unlock_path}"
        self.url = f"chrome-extension://{self.identifier}/index.html"

    async def authenticate(self) -> None:
        await self.ads.open_url(self.url)

        if await self.ads.find_element('//div[text()="Swap"]', 3):
            logger.info(f"Profile: {self.ads.label} | Rabby | Already authenticated")
            return

        await self.ads.open_url(self.unlock_url)

        await self.ads.input_text('//input[@placeholder="Enter the Password to Unlock"]', self.password)
        await self.ads.click_element('//button[span[text()="Unlock"]]')
        if not await self.ads.find_element('//div[@class="gasprice"]'):
            raise ExecutionError("Rabby auth failed")
        logger.success(f"Profile: {self.ads.label} | Rabby | Authenticated")

    # def sign(self):
    #     logger.debug(f"Profile: {self.ads.label} | Rabby | Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False
    #     sleep(2.5, 3.5)

    #     for _ in range(5):
    #         target_tab = self.ads.find_tab("notification.html", keep_focused=True)
    #         if target_tab:
    #             sleep(2, 3)
    #             if not self.ads.click_element('//button[span[text()="Sign and Create"] and not(@disabled)]', 10):
    #                 logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to sign")
    #                 break
    #             sleep(0.5, 1)
    #             self.ads.click_element('//button[text()="Confirm"]')
    #             sleep(1, 2)
    #             try:
    #                 if not self.ads.until_present('//span[text()="Transaction created"]', 25):
    #                     if self.ads.find_element('//span[text()="Fail to create"]'):
    #                         self.ads.click_element('//button[span[text()="Cancel"]]')
    #                         logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to create")
    #                         break
    #             except NoSuchWindowException:
    #                 pass
    #             signed = True
    #         sleep(1, 2)

    #     self.ads.switch_tab(current_tab)
    #     sleep(2, 3)

    #     return signed

    # def fast_sign(self):
    #     logger.debug(f"Profile: {self.ads.label} | Rabby | Fast Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False

    #     for _ in range(25000):
    #         target_tab = self.ads.find_tab("notification.html", keep_focused=True)
    #         if target_tab:
    #             logger.info(f"Profile: {self.ads.label} | Rabby | Trying to sign")
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
    #             logger.success(f"Profile: {self.ads.label} | Rabby | Transaction signed")
    #             signed = True
    #             break
    #         self.ads.switch_tab(current_tab)
    #         sleep(0.1, 0.2)

    #     return signed

    async def connect(self):
        logger.debug(f"Profile: {self.ads.label} | Rabby | Connecting")

        popup_page = await self.ads.context.wait_for_event("page", timeout=3000)
        if popup_page:
            if not await self.ads.click_element('//button[span[text()="Connect"]]', source=popup_page):
                logger.warning(f"Profile: {self.ads.label} | Rabby | Failed to sign")
                return False

        return True

    async def import_new(self, label, address, password, private_key):
        await self.ads.open_url(self.url, sleep_time=1)
        await self.ads.click_element('//button[span[text()="Next"]]', timeout=1)
        await self.ads.click_element('//button[span[text()="Get Started"]]', timeout=1)

        await self.ads.click_element('//div[text()="Import Private Key"]', timeout=1)
        await self.ads.click_element('//button[span[text()="Get Started"]]', timeout=1)

        await self.ads.click_element('//div[text()="Import Private Key"]', timeout=1)
        await self.ads.input_text('//input[@placeholder="Password must be at least 8 characters long"]', password)
        await self.ads.input_text('//input[@placeholder="Confirm password"]', password)
        await self.ads.click_element('//button[span[text()="Next"]]')

        await self.ads.input_text('//input[@placeholder="Enter your Private key"]', private_key)
        await self.ads.click_element('//button[span[text()="Confirm"]]')

        import_address = await self.ads.find_element('//div[@class="address-viewer-text subtitle"]').text

        if import_address.lower() != address.lower():
            raise ExecutionError("Address is not matching the one uner private key.")

        await self.ads.open_url(self.url)
        await self.ads.click_element('//button[@class="ant-modal-close"]', 2)
        await self.ads.click_element('//div[@class="current-address"]', 1)
        await self.ads.click_element('//div[@class="rabby-address-item-title"]', 1)
        await self.ads.click_element('//div[text()="Address Note"]//..//img', 1, sleep_time=1)

        await self.ads.click_element('//span[@class="anticon anticon-close-circle ant-input-clear-icon"]')
        await self.ads.input_text('//input[@placeholder="Please input address note"]', label)
        await self.ads.click_element('//button[span[text()="Confirm"]]')
