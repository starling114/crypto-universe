import asyncio
import os
import random
from time import sleep

import aiohttp
import playwright._impl._errors as playwright_errors
from core.tools.metamask import Metamask
from core.tools.rabby import Rabby
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    async_playwright,
)
from utils import ExecutionError, async_sleep, debug_mode, logger


class Ads:
    URL = f"http://{os.getenv('HOST_URL', 'local.adspower.net')}:{os.getenv('ADSPOWER_PORT', '50325')}/api/v1/browser"

    WALLET_RABBY = "rabby"
    WALLET_METAMASK = "metamask"
    WALLETS = {WALLET_RABBY: Rabby, WALLET_METAMASK: Metamask}
    SYSTEM_TABS = ["Rabby Offscreen Page", "DevTools"]

    def __init__(self, profile, wallet_password=None, wallet=WALLET_RABBY, label=None):
        self.profile = profile
        self.label = label or profile
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.wallet: Rabby | Metamask = None
        self._prepare_wallet(wallet, wallet_password)

    async def start(self):
        await self._start_profile()

    async def close_other_tabs(self):
        for page in self.context.pages:
            if page != self.page:
                await page.close()

    async def open_url(self, url, timeout=30, sleep_time=None):
        result = False

        awaited = await self.safe_playwright_call(
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000),
            timeout=timeout,
            name=f"open_url({url})",
            swallow_timeout=True,
        )
        result = True if awaited is not None else False

        if sleep_time:
            await async_sleep(sleep_time)

        logger.debug(f"Profile: {self.label} | {result} | Opening URL: {url}")
        return result

    async def click_element(self, selector, timeout=5, sleep_time=None, source=None):
        result = False

        element = await self.find_element(selector=selector, timeout=timeout, source=source)
        if element:
            await element.click()

            if sleep_time:
                await async_sleep(sleep_time)

            result = True

        logger.debug(f"Profile: {self.label} | {result} | Clicking element: {selector}")
        return result

    # def hover_element(self, selector, timeout=5000):
    #     """Hover over element"""
    #     logger.debug(f"Profile: {self.label} | Hovering element: {selector}")

    #     try:
    #         self.page.wait_for_selector(selector, timeout=timeout)
    #         self.page.hover(selector)
    #         return True
    #     except Exception as e:
    #         logger.error(f"Profile: {self.label} | Failed to hover element: {selector}, Error: {e}")
    #         return False

    async def input_text(self, selector, text, timeout=5, delay=0.1, sleep_time=None):
        result = False

        element = await self.find_element(selector=selector, timeout=timeout)
        if element:
            await element.fill("")
            await element.type(str(text), delay=delay)

            if sleep_time:
                await async_sleep(sleep_time)

            result = True

        logger.debug(f"Profile: {self.label} | {result} | Inputting text: {selector} -> {text}")
        return result

    async def find_element(self, selector, timeout=5, sleep_time=None, source=None):
        source = source or self.page
        element = await self.safe_playwright_call(
            source.wait_for_selector(selector, timeout=timeout * 1000),
            timeout=timeout,
            name=f"find_element({selector})",
            swallow_timeout=True,
        )

        logger.debug(f"Profile: {self.label} | {element is not None} | Locating element: {selector}")
        return element

    async def element_text(self, selector, timeout=5, sleep_time=None, source=None):
        element = await self.find_element(selector, timeout=timeout, sleep_time=sleep_time, source=source)
        result = None

        if element:
            result = await element.inner_text()
        else:
            raise ExecutionError(f"Element not found for extracting text: {selector}")

        logger.debug(f"Profile: {self.label} | {result is not None} | Getting element text: {selector} -> {result}")
        return result

    async def while_present(self, selector, timeout=5):
        result = False

        awaited = await self.safe_playwright_call(
            self.page.wait_for_selector(selector, state="detached", timeout=timeout * 1000),
            timeout=timeout,
            name=f"while_present({selector})",
            swallow_timeout=True,
        )
        result = True if awaited is not None else False

        logger.debug(f"Profile: {self.label} | While present result: {result} | Selector: {selector}")
        return result

    async def until_present(self, selector, timeout=5):
        result = False

        result = await self.find_element(selector=selector, timeout=timeout) is not None
        logger.debug(f"Profile: {self.label} | {result} | Until present: {selector}")
        return result

    # def scroll(self, direction, pixels=None, selector=None):
    #     """Scroll page or element"""
    #     logger.debug(f"Profile: {self.label} | Scrolling: {direction}")

    #     if selector is not None:
    #         element = self.page.locator(selector)
    #         if direction == "top":
    #             element.evaluate("el => el.scrollTop = 0")
    #         elif direction == "bottom":
    #             element.evaluate("el => el.scrollTop = el.scrollHeight")
    #         elif direction == "middle":
    #             element.evaluate("el => el.scrollTop = el.scrollHeight / 2")
    #         elif pixels is not None:
    #             element.evaluate(f"el => el.scrollBy(0, {pixels})")
    #         else:
    #             raise Exception("Invalid direction or missing pixels argument for scrolling the element.")
    #     else:
    #         if direction == "top":
    #             self.page.evaluate("window.scrollTo(0, 0)")
    #         elif direction == "bottom":
    #             self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    #         elif direction == "middle":
    #             self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    #         elif pixels is not None:
    #             self.page.evaluate(f"window.scrollBy(0, {pixels})")
    #         else:
    #             raise Exception("Invalid direction or missing pixels argument for scroll.")

    async def stop(self):
        await self.browser.close()
        await self.context.close()
        await self.playwright.stop()

    async def close_browser(self):
        logger.debug(f"Profile: {self.label} | Closing browser")

        try:
            for page in self.context.pages:
                await page.close()
            await self.stop()
        except Exception:
            pass

        for _ in range(3):
            data = await self._check_browser()
            if data["data"]["status"] == "Active":
                parameters = {"serial_number": self.profile}
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{Ads.URL}/stop", params=parameters) as response:
                        response.raise_for_status()
            else:
                logger.success(f"Profile: {self.label} | Closed")
                break

    # def send_key(self, key):
    #     """Send keyboard key"""
    #     self.page.keyboard.press(key)

    # def screenshot(self, folder):
    #     """Take screenshot"""
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)
    #     self.page.screenshot(path=f"{folder}/{self.label}.png")

    # def current_tab(self):
    #     """Get current page (tab)"""
    #     return self.page

    # def switch_tab(self, page_index=None, page=None):
    #     """Switch to tab by index or page object"""
    #     logger.debug(f"Profile: {self.label} | Switching tab")

    #     pages = self.context.pages
    #     if page is not None:
    #         self.page = page
    #     elif page_index is not None and 0 <= page_index < len(pages):
    #         self.page = pages[page_index]
    #     else:
    #         logger.warning(f"Profile: {self.label} | Invalid tab index or page")

    # def find_tab(self, part_of_url=None, part_of_name=None, keep_focused=False):
    #     """Find tab by URL or title"""
    #     logger.debug(f"Profile: {self.label} | Finding tab: {part_of_name}, {part_of_url}")

    #     current_page = self.page
    #     pages = self.context.pages

    #     for page in reversed(pages):
    #         try:
    #             title = page.title()
    #             url = page.url

    #             if title not in self.SYSTEM_TABS:
    #                 logger.debug(f"Profile: {self.label} | Checking page `{title}`")

    #                 if part_of_url is not None and part_of_url in url:
    #                     if keep_focused:
    #                         self.page = page
    #                     return page

    #                 if part_of_name is not None and part_of_name in title:
    #                     if keep_focused:
    #                         self.page = page
    #                     return page
    #         except:
    #             continue

    #     return None

    # def mouse_position(self):
    #     """Get mouse position"""
    #     return self.page.evaluate("() => ({x: window.mouseX || 0, y: window.mouseY || 0})")

    async def execute_script(self, script):
        result = await self.page.evaluate(script)
        logger.debug(f"Profile: {self.label} | {True} | Executing script")
        return result

    async def _start_profile(self):
        logger.debug(f"Profile: {self.label} | Starting profile")

        profile_data = await self._check_browser()
        if profile_data["data"]["status"] != "Active":
            profile_data = await self._open_browser()

        logger.success(f"Profile: {self.label} | Started")

        puppeteer_host_port = profile_data["data"]["ws"]["puppeteer"]
        host, port = puppeteer_host_port.replace("ws://", "").split(":", 1)
        puppeteer = f"ws://{os.getenv('HOST_URL', host)}:{port}"

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(puppeteer)

        if self.browser.contexts:
            self.context = self.browser.contexts[0]
        else:
            self.context = self.browser.new_context()
        self.page = await self.context.new_page()
        await self.close_other_tabs()

    async def _check_browser(self):
        try:
            logger.debug(f"Profile: {self.label} | Checking browser")
            parameters = {"serial_number": self.profile}
            headers = {}

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{Ads.URL}/active", params=parameters, headers=headers) as response:
                    response.raise_for_status()
                    json_response = await response.json()

                    if json_response["code"] == 0:
                        return json_response
                    else:
                        raise ExecutionError(json_response)
        except Exception as e:
            raise ExecutionError(f"Connection to AdsPower failed: {e}")

    async def _open_browser(self):
        try:
            logger.debug(f"Profile: {self.label} | Opening browser")
            parameters = {"serial_number": self.profile, "open_tabs": 1}
            headers = {}

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{Ads.URL}/start", params=parameters, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            raise ExecutionError(f"Connection to AdsPower failed: {e}")

    def _prepare_wallet(self, wallet_name, wallet_password):
        wallet_class = self.WALLETS.get(wallet_name)

        if wallet_class:
            self.wallet = wallet_class(self, wallet_password)
        else:
            logger.warning(f"Profile: {self.label} | Invalid wallet: {wallet_name}")

    async def safe_playwright_call(self, coro, timeout=None, name=None, swallow_timeout=True):
        name = name or repr(coro)
        try:
            if timeout is not None:
                return await asyncio.wait_for(coro, timeout=timeout)
            else:
                return await coro
        except asyncio.TimeoutError:
            if swallow_timeout:
                logger.debug(f"Timeout in Playwright call {name}")
                return None
            else:
                raise
        except playwright_errors.TimeoutError:
            if swallow_timeout:
                logger.debug(f"Playwright timeout: {name}")
                return None
            else:
                raise
        except Exception as e:
            logger.exception(f"Unexpected Playwright error in {name}: {e}")
            return None
