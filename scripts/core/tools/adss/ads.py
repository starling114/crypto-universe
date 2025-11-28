import requests
from core.tools.adss.phantom import Phantom
from core.tools.adss.rabby import Rabby
from core.tools.base_bowser import BaseBrowser
from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import INSTRUCTIONS, ExecutionError, logger, sleep


class Ads(BaseBrowser):
    WALLETS = {
        BaseBrowser.WALLET_RABBY: Rabby,
        BaseBrowser.WALLET_PHANTOM: Phantom,
    }
    SYSTEM_TABS = ["Rabby Offscreen Page", "DevTools"]

    def __init__(self, profile, wallet_password=None, wallet_type=BaseBrowser.WALLET_RABBY, label=None):
        super().__init__(
            profile=profile,
            wallet_password=wallet_password,
            wallet_type=wallet_type,
            label=label,
            wallets_config=self.WALLETS,
        )
        self.driver = self._start_profile()
        self.actions = ActionChains(self.driver)
        self._prepare_browser()

    def url(self):
        if INSTRUCTIONS.get("ads_url") and INSTRUCTIONS.get("ads_url") != "":
            base_url = INSTRUCTIONS["ads_url"]
        else:
            base_url = "http://local.adspower.net:50325"

        return f"{base_url}/api/v1"

    def open_url(self, url, timeout=30, sleep_time=None):
        try:
            if url.startswith("chrome-extension"):
                self.driver.get(url)

            self.driver.get(url)

            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if sleep_time:
                sleep(sleep_time)
        except TimeoutException:
            raise ExecutionError(f"Timeout opening url: {url}")

        logger.debug(f"Profile: {self.label} | True | Openning url: {url}")

    def find_element(self, xpath, timeout=5, sleep_time=None, source=None):
        result = None
        for _ in range(3):
            try:
                if source is not None:
                    result = source.find_element(By.XPATH, xpath)
                else:
                    result = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )

                if sleep_time:
                    sleep(sleep_time)

                break
            except TimeoutException:
                break
            except StaleElementReferenceException:
                sleep(0.5)

        logger.debug(f"Profile: {self.label} | {result is not None} | Finding element: {xpath}")
        return result

    def find_elements(self, xpath, timeout=5, sleep_time=None, source=None):
        result = []
        for _ in range(3):
            try:
                if source is not None:
                    result = source.find_elements(By.XPATH, xpath)
                else:
                    result = self.driver.find_elements(By.XPATH, xpath)

                if sleep_time:
                    sleep(sleep_time)

                break
            except StaleElementReferenceException:
                sleep(0.5)

        logger.debug(f"Profile: {self.label} | Found {len(result)} elements | Finding elements: {xpath}")
        return result

    def click_element(self, xpath, timeout=5, sleep_time=None, source=None, dom=False):
        if dom:
            try:
                result = self.execute_script(
                    f"""
                    var element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        element.click();
                        return true;
                    }} else {{
                        return false;
                    }}
                """
                )

                if sleep_time:
                    sleep(sleep_time)

                logger.debug(f"Profile: {self.label} | {result} | Clicked DOM element: {xpath}")
                return result
            except Exception as e:
                logger.error(f"Profile: {self.label} | Error clicking DOM element: {xpath} | {e}", exc_info=True)
                return False
        else:
            web_element = self.find_element(xpath=xpath, timeout=timeout, source=source)

            result = False
            if web_element:
                web_element.click()

                result = True

            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | {result} | Clicked element: {xpath}")
            return result

    def element_attribute(self, xpath, attribute, timeout=5, sleep_time=None, dom=False):
        if dom:
            result = self.execute_script(
                f"""
                var element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return element ? element.getAttribute("{attribute}") : null;
                """
            )
            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | DOM attribute: {result}")
            return result
        else:
            web_element = self.find_element(xpath=xpath, timeout=timeout)
            result = web_element.get_attribute(attribute) if web_element else None

            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | DOM attribute: {result}")
            return result

    def element_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        if dom:
            result = self.execute_script(
                f"""
                var element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return element ? element.innerText : null;
                """
            )
            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | DOM text: {result}")
            return result
        else:
            web_element = self.find_element(xpath=xpath, timeout=timeout)
            result = web_element.text if web_element else None

            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | Element text: {result}")
            return result

    def elements_text(self, xpath, timeout=5, sleep_time=None, dom=False):
        if dom:
            result = self.execute_script(
                f"""
                var xpathResult = document.evaluate("{xpath}", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                var texts = [];
                for (var i = 0; i < xpathResult.snapshotLength; i++) {{
                    var element = xpathResult.snapshotItem(i);
                    if (element) {{
                        texts.push(element.innerText);
                    }}
                }}
                return texts;
                """
            )
            if sleep_time:
                sleep(sleep_time)

            logger.debug(f"Profile: {self.label} | Found {len(result) if result else 0} DOM texts: {xpath}")
            return result or []
        else:
            web_elements = self.find_elements(xpath=xpath, timeout=timeout)
            result = [web_element.text for web_element in web_elements if web_element]
            if sleep_time:
                sleep(sleep_time)
            logger.debug(f"Profile: {self.label} | Found {len(result) if result else 0} elements text: {xpath}")
            return result or []

    def input_text(self, xpath, text, timeout=5, delay=0.1, sleep_time=None):
        web_element = self.find_element(xpath=xpath, timeout=timeout)

        result = False
        if web_element:
            for _ in range(len(web_element.get_attribute("value"))):
                web_element.send_keys(Keys.BACKSPACE)
                sleep(delay)
            web_element.clear()
            web_element.send_keys(text)
            result = True

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | {result} | Inputting text: {xpath} -> {text}")
        return result

    def while_present(self, xpath, timeout=5):
        result = False
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located((By.XPATH, xpath)))
            result = True
        except TimeoutException:
            logger.debug(f"Profile: {self.label} | Element still present after timeout: {xpath}")

        logger.debug(f"Profile: {self.label} | {result} | While present: {xpath}")
        return result

    def until_present(self, xpath, timeout=5):
        result = False
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            result = True
        except TimeoutException:
            logger.debug(f"Profile: {self.label} | Element not found after timeout: {xpath}")

        logger.debug(f"Profile: {self.label} | {result} | Until present: {xpath}")
        return result

    def send_key(self, key):
        execution_key = None
        if key == "ESC":
            execution_key = Keys.ESCAPE
        elif key == "END":
            execution_key = Keys.END
        elif execution_key == "BACKSPACE":
            execution_key = Keys.BACKSPACE
        else:
            raise ExecutionError(f"Invalid keyboard key: {key}")

        self.actions.send_keys(execution_key).perform()

    def switch_tab(self, tab):
        logger.debug(f"Profile: {self.label} | Switching tab: {tab}")
        self.driver.switch_to.window(tab)

    def new_tab(self):
        logger.debug(f"Profile: {self.label} | Opening new blank tab")
        current_tabs = self._filter_tabs()
        self.driver.execute_script("window.open('about:blank', '_blank');")
        sleep(0.5)
        new_tabs = self._filter_tabs()
        new_tab_handle = [tab for tab in new_tabs if tab not in current_tabs][0]
        self.switch_tab(new_tab_handle)
        logger.debug(f"Profile: {self.label} | New tab opened: {new_tab_handle}")
        return new_tab_handle

    def close_other_tabs(self):
        logger.debug(f"Profile: {self.label} | Closing other tabs")
        current_tab = self.current_tab()
        filtered_tabs = self._filter_tabs()
        for tab in filtered_tabs:
            if tab != current_tab:
                try:
                    self.switch_tab(tab)
                    logger.debug(f"Profile: {self.label} | Closing tab: {self.driver.title}")
                    self.driver.close()
                except Exception as e:
                    logger.error(f"Profile: {self.label} | Error closing tab: {e}", exc_info=True)
        self.switch_tab(current_tab)
        logger.debug(f"Profile: {self.label} | Other tabs closed")

    def execute_script(self, script, element=None):
        logger.debug(f"Profile: {self.label} | Executing script")
        if element is not None:
            return self.driver.execute_script(script, element)
        else:
            return self.driver.execute_script(script)

    def proxy_ip(self):
        try:
            parameters = {"serial_number": self.profile}
            response = requests.get(f"{self.url()}/user/list", params=parameters)
            response.raise_for_status()
            sleep(1)
            json_response = response.json()
            if json_response["code"] == 0:
                return json_response.get("data", {}).get("list", [])[0].get("ip")
            else:
                raise ExecutionError(json_response)
        except Exception as e:
            logger.error(f"Connection to AdsPower failed: {e}")
            return None

    def close(self):
        logger.debug(f"Profile: {self.label} | Closing browser")
        for _ in range(3):
            sleep(5)
            data = self._check_browser()
            if data["data"]["status"] == "Active":
                parameters = {"serial_number": self.profile}
                requests.get(f"{self.url()}/browser/stop", params=parameters)
            else:
                logger.success(f"Profile: {self.label} | Closed")
                break

    def current_tab(self):
        return self.driver.current_window_handle

    def find_tab(self, part_of_url=None, part_of_name=None, keep_focused=False):
        logger.debug(f"Profile: {self.label} | Finding tab: {part_of_name}, {part_of_url}")
        current_tab = self.current_tab()
        tabs = self.driver.window_handles
        for tab in reversed(tabs):
            self.switch_tab(tab)
            if self.driver.title not in self.SYSTEM_TABS:
                logger.debug(f"Profile: {self.label} | Switched to `{self.driver.title}` tab, checking...")
                if part_of_url is not None:
                    logger.debug(f"Profile: {self.label} | Checking part of url: {self.driver.current_url}")
                    if part_of_url in self.driver.current_url:
                        target_tab = self.current_tab()
                        if not keep_focused:
                            self.switch_tab(current_tab)
                        return target_tab
                if part_of_name is not None:
                    logger.debug(f"Profile: {self.label} | Checking part of name: {self.driver.title}")
                    if part_of_name in self.driver.title:
                        target_tab = self.current_tab()
                        if not keep_focused:
                            self.switch_tab(current_tab)
                        return target_tab
        return None

    def _start_profile(self):
        logger.debug(f"Profile: {self.label} | Starting profile")
        profile_data = self._check_browser()
        logger.debug(f"Browser checked: {self.label} | {profile_data}")
        if profile_data["data"]["status"] != "Active":
            profile_data = self._open_browser()
            logger.debug(f"Browser openned: {self.label} | {profile_data}")

        logger.success(f"Profile: {self.label} | Started")

        chrome_driver = profile_data["data"]["webdriver"]
        selenium_port = profile_data["data"]["ws"]["selenium"]

        service = Service(executable_path=chrome_driver)

        options = Options()
        options.add_experimental_option("debuggerAddress", selenium_port)
        options.add_experimental_option("enableExtensionTargets", True)
        options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            driver = webdriver.Chrome(options=options, service=service)
        except InvalidArgumentException as e:
            if "cannot parse capability: goog:chromeOptions" in str(e):
                options = Options()
                options.add_experimental_option("debuggerAddress", selenium_port)
                options.add_argument("--disable-blink-features=AutomationControlled")
                driver = webdriver.Chrome(options=options, service=service)
            else:
                raise e

        return driver

    def _check_browser(self):
        try:
            logger.debug(f"Profile: {self.label} | Checking browser")
            parameters = {"serial_number": self.profile}
            response = requests.get(f"{self.url()}/browser/active", params=parameters)
            response.raise_for_status()
            json_response = response.json()
            if json_response["code"] == 0:
                return response.json()
            else:
                raise ExecutionError(json_response)
        except Exception as e:
            raise ExecutionError(f"Connection to AdsPower failed: {e}")

    def _open_browser(self):
        parameters = {"serial_number": self.profile, "open_tabs": 1}
        response = requests.get(f"{self.url()}/browser/start", params=parameters)
        response.raise_for_status()
        return response.json()

    def _prepare_browser(self):
        logger.debug(f"Profile: {self.label} | Preparing browser")
        sleep(3, 4)
        tabs = self._filter_tabs()

        if len(tabs) > 1:
            for tab in tabs[1:]:
                self.switch_tab(tab)
                logger.debug(f"Profile: {self.label} | Closing `{self.driver.title}` tab")
                self.driver.close()

        self.switch_tab(tabs[0])

    def _filter_tabs(self):
        start_tabs = self.driver.window_handles
        final_tabs = []
        for tab in start_tabs:
            self.switch_tab(tab)
            logger.debug(f"Profile: {self.label} | Switched to `{self.driver.title}` tab")
            if self.driver.title not in self.SYSTEM_TABS:
                final_tabs.append(tab)

        return final_tabs
