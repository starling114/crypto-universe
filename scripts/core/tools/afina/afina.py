import playwright._impl._errors as playwright_errors
import requests
from core.tools.afina.phantom import Phantom
from core.tools.afina.rabby import Rabby
from core.tools.base_bowser import BaseBrowser
from playwright.sync_api import sync_playwright
from utils import INSTRUCTIONS, ExecutionError, logger, sleep


class Afina(BaseBrowser):
    WALLETS = {
        BaseBrowser.WALLET_RABBY: Rabby,
        BaseBrowser.WALLET_PHANTOM: Phantom,
    }

    def __init__(self, profile, wallet_password=None, wallet_type=BaseBrowser.WALLET_RABBY, label=None):
        super().__init__(
            profile=profile,
            wallet_password=wallet_password,
            wallet_type=wallet_type,
            label=label,
            wallets_config=self.WALLETS,
        )
        self.playwright = sync_playwright().start()
        self.browser = self._start_profile()

    def api_key(self):
        if INSTRUCTIONS.get("afina_api_key") and INSTRUCTIONS.get("afina_api_key") != "":
            return INSTRUCTIONS["afina_api_key"]
        else:
            raise ExecutionError("Afina API key is not set")

    def url(self):
        if INSTRUCTIONS.get("afina_url") and INSTRUCTIONS.get("afina_url") != "":
            base_url = INSTRUCTIONS["afina_url"]
        else:
            base_url = "http://127.0.0.1:50777"

        return f"{base_url}/api"

    def open_url(self, url, timeout=30, sleep_time=None):
        self._safe_playwright_call(
            lambda: self.page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000),
            name=f"open_url({url})",
        )

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | True | Openning url: {url}")

    def find_element(self, xpath, timeout=5, sleep_time=None, source=None):
        source = source or self.page
        result = self._safe_playwright_call(
            lambda: source.wait_for_selector(xpath, timeout=timeout * 1000),
            name=f"find_element({xpath})",
        )

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | {result is not None} | Finding element: {xpath}")
        return result

    def find_elements(self, xpath, timeout=5, sleep_time=None, source=None):
        source = source or self.page

        result = self._safe_playwright_call(
            lambda: source.query_selector_all(xpath),
            name=f"find_elements({xpath})",
        )

        if sleep_time:
            sleep(sleep_time)

        result = result or []

        logger.debug(f"Profile: {self.label} | Found {len(result)} elements | Finding elements: {xpath}")
        return result

    def click_element(self, xpath, timeout=5, sleep_time=None, dom=False):
        result = False

        element = self.find_element(xpath=xpath, timeout=timeout)
        if element:
            element.click()

            if sleep_time:
                sleep(sleep_time)

            result = True

        logger.debug(f"Profile: {self.label} | {result} | Clicked element: {xpath}")
        return result

    def element_attribute(self, xpath, attribute, timeout=5, sleep_time=None, dom=False):
        element = self.find_element(xpath=xpath, timeout=timeout)
        result = None
        if element:
            result = element.get_attribute(attribute)

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | DOM attribute: {result}")
        return result

    def element_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        element = self.find_element(xpath=xpath, timeout=timeout)
        result = None
        if element:
            result = element.inner_text()

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | Element text: {result}")
        return result

    def elements_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        elements = self.find_elements(xpath=xpath, timeout=timeout)
        result = []
        if elements:
            result = [element.inner_text() for element in elements]

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | Elements text: {result}")
        return result

    def input_text(self, xpath, text, timeout=5, delay=0.1, sleep_time=None):
        web_element = self.find_element(xpath=xpath, timeout=timeout)

        result = False
        if web_element:
            web_element.fill("")
            web_element.type(str(text))
            result = True

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | {result} | Inputting text: {xpath} -> {text}")
        return result

    def while_present(self, xpath, timeout=5):
        result = False

        awaited = self._safe_playwright_call(
            lambda: self.page.wait_for_selector(xpath, state="detached", timeout=timeout * 1000),
            timeout=timeout,
            name=f"while_present({xpath})",
            swallow_timeout=True,
        )
        result = True if awaited is not None else False

        logger.debug(f"Profile: {self.label} | {result} | While present: {xpath}")
        return result

    def until_present(self, xpath, timeout=5):
        result = False

        result = self.find_element(xpath=xpath, timeout=timeout) is not None
        logger.debug(f"Profile: {self.label} | {result} | Until present: {xpath}")
        return result

    def send_key(self, key):
        if key == "ESC":
            key = "Escape"
        elif key == "END":
            key = "End"
        elif key == "BACKSPACE":
            key = "Backspace"
        else:
            raise ExecutionError(f"Invalid keyboard key: {key}")

        self.page.keyboard.press(key)

    def new_tab(self):
        logger.debug(f"Profile: {self.label} | Opening new blank tab")
        new_page = self.context.new_page()
        self.page = new_page
        logger.debug(f"Profile: {self.label} | New tab opened: {new_page.url}")
        return new_page

    def switch_tab(self, page):
        logger.debug(f"Profile: {self.label} | Switching tab: {page.url}")
        self.page = page
        logger.debug(f"Profile: {self.label} | Switched to tab: {page.url}")

    def close_other_tabs(self):
        logger.debug(f"Profile: {self.label} | Closing all other tabs")

        for page in self.context.pages:
            if page != self.page:
                logger.debug(f"Profile: {self.label} | Closing tab: {page.url}")
                page.close()

        logger.debug(f"Profile: {self.label} | All other tabs closed")

    def execute_script(self, script, element=None):
        logger.debug(f"Profile: {self.label} | Executing script")
        if element is not None:
            return element.evaluate(script)
        else:
            return self.page.evaluate(script)

    def proxy_ip(self):
        try:
            logger.debug(f"Profile: {self.label} | Opening browser")

            headers = {"x-api-key": self.api_key()}
            response = requests.get(f"{self.url()}/profiles/list", headers=headers)
            response.raise_for_status()
            json_response = response.json()
            if json_response["message"] == "Accounts successfully fetched":
                for account in json_response.get("accounts", []):
                    if account.get("accountId") == self.profile:
                        return account.get("ip")

                raise ExecutionError(f"Afina account not found: {self.profile}")
            else:
                raise ExecutionError(json_response)
        except Exception as e:
            raise ExecutionError(f"Connection to Afina profile failed: {e}")

    def close(self):
        logger.debug(f"Profile: {self.label} | Closing browser")

        try:
            logger.debug(f"Profile: {self.label} | Closing browser")

            data = {"profileId": self.profile}
            headers = {"x-api-key": self.api_key()}
            response = requests.post(f"{self.url()}/profiles/stop", json=data, headers=headers)
            response.raise_for_status()
            logger.success(f"Profile: {self.label} | Closed")
        except Exception as e:
            raise ExecutionError(f"Failed to stop Afina profile: {e}")

    def _start_profile(self):
        logger.debug(f"Profile: {self.label} | Starting profile")
        profile_data = self._open_browser()
        logger.debug(f"Browser openned: {self.label} | {profile_data}")

        logger.success(f"Profile: {self.label} | Started")

        ws_endpoint = profile_data["wsEndpoint"]
        # Convert ws:// to http:// for CDP connection
        cdp_url = ws_endpoint.replace("ws://", "http://").replace("wss://", "https://")

        # Extract base URL (scheme://host:port) by removing any path
        scheme_end = cdp_url.find("://") + 3
        path_start = cdp_url.find("/", scheme_end)
        if path_start != -1:
            cdp_url = cdp_url[:path_start]

        browser = self.playwright.chromium.connect_over_cdp(cdp_url)

        if browser.contexts:
            self.context = browser.contexts[0]
        else:
            self.context = browser.new_context()
        self.page = self.context.new_page()
        self.close_other_tabs()

        return browser

    def _open_browser(self):
        try:
            logger.debug(f"Profile: {self.label} | Opening browser")

            data = {"profileId": self.profile}
            headers = {"x-api-key": self.api_key()}
            response = requests.post(f"{self.url()}/profiles/start", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ExecutionError(f"Connection to Afina profile failed: {e}")

    def _safe_playwright_call(self, func, name=None, swallow_timeout=True):
        name = name or repr(func)
        try:
            return func()
        except playwright_errors.TimeoutError:
            if swallow_timeout:
                logger.debug(f"Playwright timeout: {name}")
                return None
            else:
                raise
        except Exception as e:
            logger.exception(f"Unexpected Playwright error in {name}: {e}")
            return None
