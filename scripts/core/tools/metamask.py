from utils import logger, sleep


class Metamask:
    URL = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"

    def __init__(self, ads, password):
        self.ads = ads
        self.password = password

    async def open(self):
        await self.ads.open_url(Metamask.URL)

    async def authenticate(self) -> None:
        await self.open()

        if not await self.ads.find_element('//button[text()="Unlock"]', 2):
            logger.info(f"Profile: {self.ads.label} | Metamask | Already authenticated")
            return

        await self.ads.input_text('//input[@data-testid="unlock-password"]', self.password)
        await self.ads.click_element('//button[text()="Unlock"]')
        if not await self.ads.find_element('//button[@data-testid="account-options-menu-button"]', 15):
            raise Exception("Metamask auth failed")
        logger.success(f"Profile: {self.ads.label} | Metamask | Authenticated")

    # def sign(self):
    #     logger.debug(f"Profile: {self.ads.label} | Metamask | Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False
    #     sleep(2.5, 3.5)

    #     for _ in range(5):
    #         target_tab = self.ads.find_tab("notification.html#confirm-transaction", keep_focused=True)
    #         if target_tab:
    #             sleep(2, 3)
    #             if not self.ads.click_element('//button[text()="Confirm" and not(@disabled)]', 10):
    #                 logger.warning(f"Profile: {self.ads.label} | Metamask | Failed to sign")
    #             else:
    #                 signed = True
    #             sleep(1, 2)
    #             break
    #         sleep(1, 2)

    #     self.ads.switch_tab(current_tab)
    #     sleep(2, 3)

    #     return signed

    # def fast_sign(self, gas_type=None, max_base_fee=None, priority_fee=None, gas_limit=None):
    #     logger.debug(f"Profile: {self.ads.label} | Metamask | Fast Signing transaction")
    #     current_tab = self.ads.current_tab()
    #     signed = False

    #     for _ in range(25000):
    #         target_tab = self.ads.find_tab("notification.html#confirm-transaction", keep_focused=True)
    #         if target_tab:
    #             logger.info(f"Profile: {self.ads.label} | Metamask | Trying to sign")

    #             if gas_type:
    #                 if not self.ads.click_element('//button[@data-testid="edit-gas-fee-icon"]'):
    #                     logger.info(f"Profile: {self.ads.label} | Metamask | Failed to edit gas fee")
    #                 else:
    #                     self.ads.click_element(f"//span[contains(text(), '{gas_type}')]")

    #                     if gas_type == "Advanced":
    #                         # TODO: Instead custom provide ability to do xN greater than aggressive
    #                         if max_base_fee:
    #                             self.ads.input_text('//input[@data-testid="base-fee-input"]', max_base_fee, 1, delay=0)
    #                         if priority_fee:
    #                             self.ads.input_text(
    #                                 '//input[@data-testid="priority-fee-input"]', priority_fee, 1, delay=0
    #                             )
    #                         if gas_limit:
    #                             self.ads.click_element('//a[text()="Edit"]', 1)
    #                             self.ads.input_text('//input[@data-testid="gas-limit-input"]', gas_limit, 1, delay=0)
    #                         self.ads.click_element('//button[text()="Save"]')

    #             if not self.ads.click_element('//button[text()="Confirm" and not(@disabled)]', 10):
    #                 logger.warning(f"Profile: {self.ads.label} | Metamask | Failed to sign")
    #             else:
    #                 logger.success(f"Profile: {self.ads.label} | Rabby | Transaction signed")
    #                 signed = True
    #             break
    #         sleep(0.1, 0.2)

    #     self.ads.switch_tab(current_tab)
    #     sleep(2, 3)

    #     return signed
