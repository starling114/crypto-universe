import requests
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

from utils import sleep, logger, ExecutionError
from core.tools.rabby import Rabby
from core.tools.metamask import Metamask


class Ads:
    URL = "http://local.adspower.net:50325/api/v1/browser"
    WALLET_RABBY = "rabby"
    WALLET_METAMASK = "metamask"
    WALLETS = {WALLET_RABBY: Rabby, WALLET_METAMASK: Metamask}

    def __init__(self, profile, wallet_password=None, wallet=WALLET_RABBY):
        self.profile = profile
        self.driver = self._start_profile()
        self.actions = ActionChains(self.driver)
        self._prepare_browser()
        self._prepare_wallet(wallet, wallet_password)

    def open_url(self, url, xpath=None, timeout=30, track_mouse=False):
        logger.debug(f"Profile: {self.profile} | Openning url: {url}")
        if url.startswith("chrome-extension"):
            self.driver.get(url)

        self.driver.get(url)

        if xpath is not None:
            self.find_element(xpath, timeout)

        if track_mouse:
            self._track_mouse_position()

    def click_element(self, xpath, timeout=5, random_place=False):
        logger.debug(f"Profile: {self.profile} | Clicking element: {xpath}")
        web_element = self.find_element(xpath, timeout)
        if web_element:

            if random_place:
                middle_width = (web_element.size["width"] // 2) - 5
                middle_height = (web_element.size["height"] // 2) - 5

                random_x = random.randint(-middle_width, middle_width)
                random_y = random.randint(-middle_height, middle_height)

                self.actions.move_to_element_with_offset(web_element, random_x, random_y).click().perform()
            else:
                web_element.click()

            return True
        else:
            return False

    def hover_element(self, xpath, timeout=5):
        logger.debug(f"Profile: {self.profile} | Hovering element: {xpath}")
        web_element = self.find_element(xpath, timeout)
        if web_element:
            self.actions.move_to_element(web_element).perform()
            return True
        else:
            return False

    def input_text(self, xpath, text, timeout=5, delay=0.1):
        logger.debug(f"Profile: {self.profile} | Inputting text: {xpath} -> {text}")
        web_element = self.find_element(xpath, timeout)
        if web_element:
            web_element.clear()
            for letter in str(text):
                web_element.send_keys(letter)
                sleep(delay)
            return True
        else:
            return False

    def find_element(self, xpath, timeout=5):
        logger.debug(f"Profile: {self.profile} | Finding element: {xpath}")
        for _ in range(timeout):
            try:
                return self.driver.find_element(By.XPATH, xpath)
            except NoSuchElementException:
                sleep(0.5, 1)
        return None

    def while_present(self, xpath, timeout=5):
        logger.debug(f"Profile: {self.profile} | While present: {xpath}")
        for _ in range(timeout):
            try:
                self.driver.find_element(By.XPATH, xpath)
                sleep(0.5, 1)
            except NoSuchElementException:
                return True

        return False

    def until_present(self, xpath, timeout=5):
        logger.debug(f"Profile: {self.profile} | Until present: {xpath}")
        for _ in range(timeout):
            element = self.find_element(xpath, timeout)

            if element is not None:
                return True

        return False

    def scroll(self, direction=None, pixels=None):
        logger.debug(f"Profile: {self.profile} | Scrolling: {direction}")
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
        logger.debug(f"Profile: {self.profile} | Closing browser")
        for _ in range(3):
            sleep(5)
            data = self._check_browser()
            if data["data"]["status"] == "Active":
                parameters = {"serial_number": self.profile}
                requests.get(f"{Ads.URL}/stop", params=parameters)
            else:
                logger.success(f"Profile: {self.profile} | Closed")
                break

    def current_tab(self):
        return self.driver.current_window_handle

    def switch_tab(self, tab):
        logger.debug(f"Profile: {self.profile} | Switching tab")
        self.driver.switch_to.window(tab)

    def find_tab(self, part_of_url=None, part_of_name=None, keep_focused=False):
        logger.debug(f"Profile: {self.profile} | Finding tab: {part_of_name}, {part_of_url}")
        current_tab = self.current_tab()
        for tab in self._filter_tabs():
            self.switch_tab(tab)
            if part_of_url is not None:
                if part_of_url in self.driver.current_url:
                    target_tab = self.current_tab()
                    if not keep_focused:
                        self.switch_tab(current_tab)
                    return target_tab
            if part_of_name is not None:
                if part_of_name in self.driver.title:
                    target_tab = self.current_tab()
                    if not keep_focused:
                        self.switch_tab(current_tab)
                    return target_tab
        return None

    def mouse_position(self):
        return self.driver.execute_script("return {x: window.mouseX, y: window.mouseY};")

    def execute_script(self, script):
        logger.debug(f"Profile: {self.profile} | Executing script")
        self.driver.execute_script(script)

    def _start_profile(self):
        logger.debug(f"Profile: {self.profile} | Starting profile")
        profile_data = self._check_browser()
        if profile_data["data"]["status"] != "Active":
            profile_data = self._open_browser()

        logger.success(f"Profile: {self.profile} | Started")

        chrome_driver = profile_data["data"]["webdriver"]
        selenium_port = profile_data["data"]["ws"]["selenium"]

        service = Service(executable_path=chrome_driver)

        options = Options()
        options.add_experimental_option("debuggerAddress", selenium_port)
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(options=options, service=service)
        return driver

    def _check_browser(self):
        try:
            logger.debug(f"Profile: {self.profile} | Checking browser")
            parameters = {"serial_number": self.profile}
            response = requests.get(f"{Ads.URL}/active", params=parameters)
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
        response = requests.get(f"{Ads.URL}/start", params=parameters)
        response.raise_for_status()
        return response.json()

    def _prepare_browser(self):
        logger.debug(f"Profile: {self.profile} | Preparing browser")
        sleep(3, 4)
        tabs = self._filter_tabs()

        if len(tabs) > 1:
            for tab in tabs[1:]:
                self.switch_tab(tab)
                logger.debug(f"Profile: {self.profile} | Closing `{self.driver.title}` tab")
                self.driver.close()

        self.switch_tab(tabs[0])
        self.driver.maximize_window()

    def _prepare_wallet(self, wallet_name, wallet_password):
        wallet = self.WALLETS.get(wallet_name)

        if wallet:
            self.wallet = wallet(self, wallet_password)
        else:
            raise ExecutionError(f"Invalid wallet: {wallet_name}")

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
            logger.debug(f"Profile: {self.profile} | Switched to `{self.driver.title}` tab")
            if self.driver.title not in ["Rabby Offscreen Page", "DevTools"]:
                final_tabs.append(tab)

        return final_tabs
