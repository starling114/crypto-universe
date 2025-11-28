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
            else:
                self.ads.input_text('//input[@data-testid="unlock-form-password-input"]', self.password)
                self.ads.click_element('//button[@data-testid="unlock-form-submit-button"]')
                self.ads.click_element('//div[@id="modal"]//div[2]//div//div', 3)
                if not self.ads.until_present('//div[text()="Receive"]', 3):
                    raise ExecutionError("Phantom auth failed")

                self._is_authenticated = True
                logger.success(f"Profile: {self.ads.label} | Phantom | Authenticated")

            self.ads.new_tab()
            self.ads.close_other_tabs()

    def import_new(self, label, address, password, recovery_phrase):
        self.ads.open_url(f"chrome-extension://{self.identifier}/onboarding.html")
        sleep(1, 2)

        self.ads.click_element('//button[text()="I already have a wallet"]')
        self.ads.click_element('//div[text()="Import Recovery Phrase"]')

        for i, word in enumerate(recovery_phrase.split(" ")):
            self.ads.input_text(f"//input[@data-testid='secret-recovery-phrase-word-input-{i}']", word)

        self.ads.click_element('//button[text()="Import Wallet"]')
        self.ads.click_element('//button[text()="Continue"]')

        self.ads.input_text('//input[@data-testid="onboarding-form-password-input"]', password)
        self.ads.input_text('//input[@data-testid="onboarding-form-confirm-password-input"]', password)
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

        self.ads.input_text('//input[@name="name"]', label)
        self.ads.click_element('//button[text()="Save"]', sleep_time=0.3)
