from utils import ExecutionError


class BaseBrowser:
    WALLET_RABBY = "rabby"
    WALLET_PHANTOM = "phantom"
    SYSTEM_TABS = ["Rabby Offscreen Page", "DevTools"]

    def __init__(self, profile, wallet_password=None, wallet_type=WALLET_RABBY, label=None, wallets_config={}):
        self.profile = profile
        self.label = label or profile
        self.wallet_password = wallet_password
        self.wallets_config = wallets_config
        self.wallet_type = None
        self.change_wallet(wallet_type)

    def url(self):
        raise NotImplementedError

    def open_url(self, url, timeout=30, sleep_time=None):
        raise NotImplementedError

    def find_element(self, xpath, timeout=5, sleep_time=None, source=None):
        raise NotImplementedError

    def find_elements(self, xpath, timeout=5, sleep_time=None, source=None):
        raise NotImplementedError

    def click_element(self, xpath, timeout=5, sleep_time=None, source=None, dom=False):
        raise NotImplementedError

    def element_attribute(self, xpath, attribute, timeout=5, sleep_time=None, dom=False):
        raise NotImplementedError

    def element_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        raise NotImplementedError

    def elements_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        raise NotImplementedError

    def input_text(self, xpath, text, timeout=5, delay=0.1, sleep_time=None):
        raise NotImplementedError

    def while_present(self, xpath, timeout=5):
        raise NotImplementedError

    def until_present(self, xpath, timeout=5):
        raise NotImplementedError

    def send_key(self, key):
        raise NotImplementedError

    def switch_tab(self, tab):
        raise NotImplementedError

    def new_tab(self):
        raise NotImplementedError

    def close_other_tabs(self):
        raise NotImplementedError

    def execute_script(self, script, element=None):
        raise NotImplementedError

    def proxy_ip(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def change_wallet(self, wallet_type):
        if wallet_type == self.wallet_type:
            return

        wallet = self.wallets_config.get(wallet_type)

        if wallet:
            self.wallet = wallet(self, self.wallet_password)
            self.wallet_type = wallet_type
        else:
            raise ExecutionError(f"Invalid wallet: {wallet_type}")
