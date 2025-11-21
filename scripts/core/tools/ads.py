import os

import requests
from core.tools.metamask import Metamask
from core.tools.phantom import Phantom
from core.tools.rabby import Rabby
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


class Ads:
    WALLET_RABBY = "rabby"
    WALLET_METAMASK = "metamask"
    WALLET_PHANTOM = "phantom"
    WALLETS = {WALLET_RABBY: Rabby, WALLET_METAMASK: Metamask, WALLET_PHANTOM: Phantom}
    SYSTEM_TABS = ["Rabby Offscreen Page", "DevTools"]

    def __init__(self, profile, wallet_password=None, wallet_type=WALLET_RABBY, label=None):
        self.profile = profile
        self.label = label or profile
        self.driver = self._start_profile()
        self.actions = ActionChains(self.driver)
        self.wallet_password = wallet_password
        self.wallet_type = None
        self.wallet: Rabby | Metamask = None
        self._prepare_browser()
        self.change_wallet(wallet_type)

    def url(self):
        if INSTRUCTIONS["ads_url"] and INSTRUCTIONS["ads_url"] != "":
            base_url = INSTRUCTIONS["ads_url"]
        else:
            base_url = "http://local.adspower.net:50325"

        return f"{base_url}/api/v1"

    def open_url(self, url, timeout=30, track_mouse=False, sleep_time=None):
        try:
            if url.startswith("chrome-extension"):
                self.driver.get(url)

            self.driver.get(url)

            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if track_mouse:
                self._track_mouse_position()

            if sleep_time:
                sleep(sleep_time)
        except TimeoutException:
            raise ExecutionError(f"Timeout opening url: {url}")

        logger.debug(f"Profile: {self.label} | True | Openning url: {url}")

    def find_element(self, xpath, timeout=5, sleep_time=None, source=None, retries=3):
        result = None
        for _ in range(retries):
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

    def click_element(self, xpath, timeout=5, sleep_time=None):
        web_element = self.find_element(xpath, timeout)

        result = False
        if web_element:
            web_element.click()

            result = True

        if sleep_time:
            sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | {result} | Clicking element: {xpath}")
        return result

    def text_from_dom(self, xpath):
        logger.debug(f"Profile: {self.label} | Getting DOM text: {xpath}")
        return self.execute_script(
            f"""
            var element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return element ? element.textContent : null;
        """
        )

    def click_element_dom(self, xpath):
        logger.debug(f"Profile: {self.label} | Clicking DOM element: {xpath}")
        try:
            self.execute_script(
                f"""
                var element = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return element ? element.click() : null;
            """
            )
            return True
        except Exception as e:
            logger.error(f"Profile: {self.label} | Error clicking DOM element: {xpath} | {e}")
            return False

    def hover_element(self, xpath, timeout=5):
        web_element = self.find_element(xpath, timeout)

        result = False
        if web_element:
            self.actions.move_to_element(web_element).perform()
            result = True
        else:
            result = False

        logger.debug(f"Profile: {self.label} | {result} | Hovering element: {xpath}")
        return result

    def input_text(self, xpath, text, timeout=5, delay=0.1, single=False, sleep_time=None):
        web_element = self.find_element(xpath, timeout)

        result = False
        if web_element:
            if single:
                for _ in range(len(web_element.get_attribute("value"))):
                    web_element.send_keys(Keys.BACKSPACE)
                    sleep(delay)
                web_element.clear()
                web_element.send_keys(text)
            else:
                web_element.clear()
                for letter in str(text):
                    web_element.send_keys(letter)
                    sleep(delay)
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

    def scroll(self, direction, pixels=None, xpath=None):
        logger.debug(f"Profile: {self.label} | Scrolling: {direction}")
        if xpath is not None:
            element = self.find_element(xpath)
            if element is not None:
                if direction == "top":
                    self.driver.execute_script("arguments[0].scrollTop = 0;", element)
                elif direction == "bottom":
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
                elif direction == "middle":
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 2;", element)
                elif pixels is not None:
                    self.driver.execute_script(f"arguments[0].scrollBy(0, {pixels});", element)
                else:
                    raise ExecutionError("Invalid direction or missing pixels argument for scrolling the element.")
        else:
            if direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "middle":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            elif pixels is not None:
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            else:
                Exception("Invalid direction or missing pixels argument for scroll.")

        # TODO: Implement move mouse events
        # def move_mouse(self, element, duration=2, steps=3):
        #   actions = ActionChains(self.driver)

        #   location = element.location
        #   size = element.size

        #   start_x = 989
        #   start_y = 760

        #   # Calculate the center of the element
        #   end_x = location['x'] + size['width'] // 2
        #   end_y = location['y'] + size['height'] // 2

        #   delta_x = (end_x - start_x) // steps
        #   delta_y = (end_y - start_y) // steps

        #   x_position, y_position = start_x, start_y
        #   logger.info(f"Delta - x: {delta_x}, y: {delta_y}")
        #   logger.info(f"Start - x: {x_position}, y: {y_position}")

        #   # Ensure the initial position is within bounds
        #   if not (0 <= x_position < self.driver.execute_script('return window.innerWidth') and
        #           0 <= y_position < self.driver.execute_script('return window.innerHeight')):
        #       logger.error("Start position out of bounds!")
        #       return

        #   for i in range(steps):
        #       x_position += delta_x
        #       y_position += delta_y

        #       logger.info(f"Move - x: {x_position}, y: {y_position}")

        #       if not (0 <= x_position < self.driver.execute_script('return window.innerWidth') and
        #               0 <= y_position < self.driver.execute_script('return window.innerHeight')):
        #           logger.error("Move target out of bounds!")
        #           break

        #       actions.move_by_offset(delta_x, delta_y).perform()
        #       logger.success("Moved")

        #       sleep(duration / steps)

        #   logger.info(f"End - x: {x_position}, y: {y_position}")
        #   actions.move_to_element(element).perform()
        #   sleep(1)

    def close_browser(self):
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

    def send_key(self, key):
        self.actions.send_keys(key).perform()

    def screenshot(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.driver.save_screenshot(f"{folder}/{self.label}.png")

    def current_tab(self):
        return self.driver.current_window_handle

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

    def close_all_other_tabs(self):
        logger.debug(f"Profile: {self.label} | Closing all other tabs")
        current_tab = self.current_tab()
        filtered_tabs = self._filter_tabs()
        for tab in filtered_tabs:
            if tab != current_tab:
                try:
                    self.switch_tab(tab)
                    logger.debug(f"Profile: {self.label} | Closing tab: {self.driver.title}")
                    self.driver.close()
                except Exception as e:
                    logger.debug(f"Profile: {self.label} | Error closing tab: {e}")
        self.switch_tab(current_tab)
        logger.debug(f"Profile: {self.label} | All other tabs closed")

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

    def mouse_position(self):
        return self.driver.execute_script("return {x: window.mouseX, y: window.mouseY};")

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

    def change_wallet(self, wallet_type):
        if wallet_type == self.wallet_type:
            return

        wallet = self.WALLETS.get(wallet_type)

        if wallet:
            self.wallet = wallet(self, self.wallet_password)
            self.wallet_type = wallet_type
        else:
            raise ExecutionError(f"Invalid wallet: {wallet_type}")

    def _track_mouse_position(self):
        self.execute_script(
            """
                document.addEventListener('mousemove', function(event) {
                    window.mouseX = event.clientX;
                    window.mouseY = event.clientY;
                });
            """
        )

    def _filter_tabs(self):
        start_tabs = self.driver.window_handles
        final_tabs = []
        for tab in start_tabs:
            self.switch_tab(tab)
            logger.debug(f"Profile: {self.label} | Switched to `{self.driver.title}` tab")
            if self.driver.title not in self.SYSTEM_TABS:
                final_tabs.append(tab)

        return final_tabs
        return final_tabs
