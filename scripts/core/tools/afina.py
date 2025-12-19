import requests
from core.tools.browser import Browser
from utils import INSTRUCTIONS, ExecutionError, logger, sleep


class Afina(Browser):
    def api_key(self):
        if INSTRUCTIONS.get("afina_api_key") and INSTRUCTIONS.get("afina_api_key") != "":
            return INSTRUCTIONS["afina_api_key"]
        else:
            raise ExecutionError("Afina API key is not set")

    def url(self):
        return "http://127.0.0.1:50777/api"

    def _start_profile(self):
        logger.debug(f"Profile: {self.label} | Starting profile")

        profile_data = self._open_browser()
        logger.debug(f"Browser openned: {self.label} | {profile_data}")

        logger.success(f"Profile: {self.label} | Started")

        ws_endpoint = profile_data["wsEndpoint"]

        selenium_host = ws_endpoint.replace("ws://", "").split("/")[0].split(":")[0]
        selenium_port = profile_data["port"]
        debug_address = f"{selenium_host}:{selenium_port}"
        chrome_driver = profile_data["data"]["webdriver"]

        return super()._start_profile(chrome_driver, debug_address)

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
        try:
            logger.debug(f"Profile: {self.label} | Closing browser")

            data = {"profileId": self.profile}
            headers = {"x-api-key": self.api_key()}
            response = requests.post(f"{self.url()}/profiles/stop", json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ExecutionError(f"Connection to Afina profile failed: {e}")

    def proxy_ip(self):
        try:
            logger.debug(f"Profile: {self.label} | Getting proxy IP")

            headers = {"x-api-key": self.api_key()}
            response = requests.get(f"{self.url()}/profiles/get", params={"accountId": self.profile}, headers=headers)
            response.raise_for_status()
            json = response.json()

            if json.get("message") == "Account successfully fetched":
                return json.get("profile", {}).get("proxy", {}).get("host")
            else:
                raise ExecutionError(json.get("message"))
        except Exception as e:
            raise ExecutionError(f"Connection to Afina profile failed: {e}")
