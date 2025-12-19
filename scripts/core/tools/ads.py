import requests
from core.tools.browser import Browser
from utils import INSTRUCTIONS, ExecutionError, logger, sleep


class Ads(Browser):
    def url(self):
        if INSTRUCTIONS["ads_url"] and INSTRUCTIONS["ads_url"] != "":
            base_url = INSTRUCTIONS["ads_url"]
        else:
            base_url = "http://local.adspower.net:50325"

        return f"{base_url}/api/v1"

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

        return super()._start_profile(chrome_driver, selenium_port)

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
