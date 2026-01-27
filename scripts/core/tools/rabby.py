import os

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
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

    def notification_url(self):
        return f"chrome-extension://{self.identifier}/notification.html"

    def authenticate(self) -> None:
        if self._is_authenticated:
            return

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(self.browser._cdp_endpoint)
                context = browser.contexts[0]

                page = None
                for pg in context.pages:
                    if self.identifier in pg.url and "offscreen.html" not in pg.url:
                        page = pg
                        break
                if not page:
                    page = context.new_page()

                page.goto(self.url(), wait_until="domcontentloaded", timeout=30000)
                sleep(2)

                swap_element = page.locator('//div[text()="Swap"]')
                if swap_element.count() > 0:
                    logger.info(f"Profile: {self.browser.label} | Rabby | Already authenticated")
                    page.close()
                    self._is_authenticated = True
                    return

                page.goto(self.unlock_url(), wait_until="domcontentloaded", timeout=30000)
                sleep(1)

                password_input = page.locator('//input[@placeholder="Enter the Password to Unlock"]')
                password_input.fill(self.password)

                unlock_btn = page.locator('//button[span[text()="Unlock"]]')
                unlock_btn.click()

                try:
                    page.locator('//div[text()="Swap"]').wait_for(timeout=15000)
                    logger.success(f"Profile: {self.browser.label} | Rabby | Authenticated")
                    page.close()
                    self._is_authenticated = True
                except PlaywrightTimeout:
                    raise ExecutionError("Rabby auth failed - timeout waiting for Swap element")

            self.browser.close_all_other_tabs()
        except Exception as e:
            logger.error(f"Profile: {self.browser.label} | Rabby auth error: {e}")
            raise ExecutionError(f"Rabby auth failed: {e}")

    def sign(self):
        logger.debug(f"Profile: {self.browser.label} | Rabby | Signing transaction")
        current_tab = self.browser.current_tab()
        signed = False

        for _ in range(5):
            target_tab = self.browser.find_tab("notification.html", keep_focused=True)
            if target_tab:
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.connect_over_cdp(self.browser._cdp_endpoint)
                        context = browser.contexts[0]

                        page = None
                        for pg in context.pages:
                            if self.identifier in pg.url and "notification.html" in pg.url:
                                page = pg
                                break
                        if not page:
                            page = context.new_page()
                            page.goto(self.notification_url(), wait_until="domcontentloaded", timeout=30000)

                        sleep(1)

                        sign_btn = page.locator('//button[span[contains(text(), "Sign")] and not(@disabled)]')
                        if sign_btn.count() == 0:
                            logger.warning(f"Profile: {self.browser.label} | Rabby | Sign button not found")
                            break

                        sign_btn.click()
                        sleep(0.5, 1)

                        confirm_btn = page.locator('//button[text()="Confirm"]')
                        if confirm_btn.count() > 0:
                            confirm_btn.click()

                        try:
                            page.locator('//span[text()="Transaction created"]').wait_for(timeout=25000)
                            signed = True
                        except PlaywrightTimeout:
                            if page.locator('//span[text()="Fail to create"]').count() > 0:
                                cancel_btn = page.locator('//button[span[text()="Cancel"]]')
                                if cancel_btn.count() > 0:
                                    cancel_btn.click()
                                logger.warning(f"Profile: {self.browser.label} | Rabby | Failed to create")

                    break
                except Exception as e:
                    logger.warning(f"Profile: {self.browser.label} | Rabby | Sign error: {e}")
                    break

            sleep(1)

        self.browser.switch_tab(current_tab)
        return signed

    def connect(self):
        logger.debug(f"Profile: {self.browser.label} | Rabby | Connecting")
        current_tab = self.browser.current_tab()
        connected = False

        for _ in range(1):
            target_tab = self.browser.find_tab("notification.html#/approval", keep_focused=True)
            if target_tab:
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.connect_over_cdp(self.browser._cdp_endpoint)
                        context = browser.contexts[0]

                        page = None
                        for pg in context.pages:
                            if self.identifier in pg.url and "notification.html" in pg.url:
                                page = pg
                                break
                        if not page:
                            page = context.new_page()
                            page.goto(
                                f"{self.notification_url()}#/approval", wait_until="domcontentloaded", timeout=30000
                            )

                        sleep(1)

                        connect_btn = page.locator('//button[span[text()="Connect"]]')
                        if connect_btn.count() > 0:
                            connect_btn.click()
                            sleep(0.5, 1)
                            connected = True
                        else:
                            logger.warning(f"Profile: {self.browser.label} | Rabby | Connect button not found")

                    break
                except Exception as e:
                    logger.warning(f"Profile: {self.browser.label} | Rabby | Connect error: {e}")
                    break

            sleep(1)

        self.browser.switch_tab(current_tab)
        return connected

    def import_new(self, label, address, password, private_key):
        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(self.browser._cdp_endpoint)
                context = browser.contexts[0]

                page = context.new_page()
                page.goto(self.url(), wait_until="domcontentloaded", timeout=30000)
                sleep(1, 2)

                next_btn = page.locator('//button[span[text()="Next"]]')
                if next_btn.count() > 0:
                    next_btn.click()
                    sleep(0.5)

                get_started_btn = page.locator('//button[span[text()="Get Started"]]')
                if get_started_btn.count() > 0:
                    get_started_btn.click()
                    sleep(0.5)

                import_pk_btn = page.locator('//div[text()="Import Private Key"]')
                if import_pk_btn.count() > 0:
                    import_pk_btn.click()
                    sleep(0.5)

                get_started_btn = page.locator('//button[span[text()="Get Started"]]')
                if get_started_btn.count() > 0:
                    get_started_btn.click()
                    sleep(0.5)

                import_pk_btn = page.locator('//div[text()="Import Private Key"]')
                if import_pk_btn.count() > 0:
                    import_pk_btn.click()
                    sleep(0.5)

                password_input = page.locator('//input[@placeholder="Password must be at least 8 characters long"]')
                password_input.fill(password)

                confirm_password_input = page.locator('//input[@placeholder="Confirm password"]')
                confirm_password_input.fill(password)

                next_btn = page.locator('//button[span[text()="Next"]]')
                next_btn.click()
                sleep(0.5)

                pk_input = page.locator('//input[@placeholder="Enter your Private key"]')
                pk_input.fill(private_key)

                confirm_btn = page.locator('//button[span[text()="Confirm"]]')
                confirm_btn.click()
                sleep(1)

                address_element = page.locator('//div[@class="address-viewer-text subtitle"]')
                import_address = address_element.text_content()

                if import_address.lower() != address.lower():
                    page.close()
                    raise ExecutionError("Address is not matching the one under private key.")

                page.goto(self.url(), wait_until="domcontentloaded")
                sleep(1)

                close_modal_btn = page.locator('//button[@class="ant-modal-close"]')
                if close_modal_btn.count() > 0:
                    close_modal_btn.click()
                    sleep(0.5)

                current_address = page.locator('//div[@class="current-address"]')
                if current_address.count() > 0:
                    current_address.click()
                    sleep(0.5)

                address_item = page.locator('//div[@class="rabby-address-item-title"]')
                if address_item.count() > 0:
                    address_item.click()
                    sleep(0.5)

                address_note_btn = page.locator('//div[text()="Address Note"]//..//img')
                if address_note_btn.count() > 0:
                    address_note_btn.click()
                    sleep(1, 2)

                clear_btn = page.locator('//span[@class="anticon anticon-close-circle ant-input-clear-icon"]')
                if clear_btn.count() > 0:
                    clear_btn.click()
                    sleep(0.3)

                note_input = page.locator('//input[@placeholder="Please input address note"]')
                note_input.fill(label)

                confirm_btn = page.locator('//button[span[text()="Confirm"]]')
                confirm_btn.click()

                page.close()
        except ExecutionError:
            raise
        except Exception as e:
            logger.error(f"Profile: {self.browser.label} | Rabby import error: {e}")
            raise ExecutionError(f"Rabby import failed: {e}")
