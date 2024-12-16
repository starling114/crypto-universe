from utils import logger, sleep


class Rabby:
    URL = "chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/popup.html"

    def __init__(self, ads, password=None, seed=None):
        self.ads = ads
        self.password = password
        self.seed = seed

    def open(self):
        self.ads.open_url(Rabby.URL)

    def authenticate(self) -> None:
        self.open()

        if not self.ads.find_element('//button[span[text()="Unlock"]]', 2):
            logger.info(f"Profile: {self.ads.profile_number} | Rabby | Already authenticated")
            return

        self.ads.input_text('//input[@placeholder="Enter the Password to Unlock"]', self.password)
        self.ads.click_element('//button[span[text()="Unlock"]]')
        if not self.ads.find_element('//div[@class="gasprice"]', 15):
            raise Exception("Rabby auth failed")
        logger.success(f"Profile: {self.ads.profile_number} | Rabby | Authenticated")

    def sign(self):
        logger.debug(f"Profile: {self.ads.profile_number} | Rabby | Signing transaction")
        current_tab = self.ads.current_tab()
        sleep(2.5, 3.5)

        for _ in range(5):
            target_tab = self.ads.find_tab("notification.html", keep_focused=True)
            if target_tab:
                sleep(1.5, 2.5)
                self.ads.click_element('//button[span[text()="Sign and Create"]]')
                sleep(0.5, 1.5)
                self.ads.click_element('//button[text()="Confirm"]')
                sleep(2, 3)
                self.ads.switch_tab(current_tab)
                sleep(2.5, 3.5)
                break
            sleep(2, 3)
