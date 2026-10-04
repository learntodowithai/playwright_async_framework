from pathlib import Path
from typing import Optional, Union, Any
from playwright.async_api import Page, Locator, expect
import allure
import json
import os

from config.settings import settings

FlexibleLocator = Union[str, Locator]
should_highlight = os.getenv('HIGHLIGHT', 'false').lower() == 'true'


class BasePage:
    """Base page object with common functionality."""
    def __init__(self, page: Page, timeout: int = 30000):
        self.page = page
        self.default_timeout = timeout

    async def _highlight_element(self, locator: FlexibleLocator, index: Optional[int] = None) -> None:
        if not should_highlight:
            return
        try:
            loc = self._get_locator(locator, index)
            await loc.evaluate("""
            (el) => {
                el.style.outline = '3px solid blue';
                el.style.outlineOffset = '2px';
                el.style.boxShadow = '0 0 0 3px rgba(0,0,255,0.4)';
            }
            """)
        except Exception:
            pass

    @allure.step("{action} with {msg} ")
    async def _run_with_reporting(self, action, msg: Optional[str] = None):
        return await action()

    @allure.step(" {locator} with index: {index}")
    def _get_locator(self, locator: FlexibleLocator, index: Optional[int] = None) -> Locator:
        if isinstance(locator, str):
            loc = self.page.locator(locator)
        else:
            loc = locator
        return loc.nth(index) if index is not None else loc.first

    async def _scroll_if_needed(self, locator: FlexibleLocator, index: Optional[int] = None):
        try:
            await self._get_locator(locator, index).scroll_into_view_if_needed()
        except Exception:
            pass

    async def click(self, locator: FlexibleLocator, msg: str | None = None,
                    force: bool = False, timeout: Optional[int] = None,
                    index: Optional[int] = None):
        await self._highlight_element(locator, index)
        await self._scroll_if_needed(locator, index)
        await self._get_locator(locator, index).click(
            force=force,
            timeout=timeout or self.default_timeout
        )

    async def double_click(self, locator: FlexibleLocator, msg: str | None = None):
        await self._get_locator(locator).dblclick(timeout=self.default_timeout)

    async def right_click(self, locator: FlexibleLocator, msg: str | None = None):
        await self._get_locator(locator).click(button='right', timeout=self.default_timeout)

    async def fill(self, locator: FlexibleLocator, text: str, msg: str | None = None):
        await self._get_locator(locator).fill(text, timeout=self.default_timeout)

    async def type(self, locator: FlexibleLocator, text: str,
                   msg: str | None = None, delay: int = 500):
        await self._get_locator(locator).press_sequentially(
            text, delay=delay, timeout=self.default_timeout
        )

    async def hover(self, locator: FlexibleLocator):
        await self._get_locator(locator).hover(timeout=self.default_timeout)

    async def clear(self, locator: FlexibleLocator):
        await self._get_locator(locator).clear(timeout=self.default_timeout)

    async def get_text(self, locator: FlexibleLocator) -> Optional[str]:
        return await self._get_locator(locator).text_content(timeout=self.default_timeout)

    async def get_inner_text(self, locator: FlexibleLocator) -> str:
        return (await self._get_locator(locator).inner_text(timeout=self.default_timeout)).strip()

    async def get_attribute_value(self, locator: FlexibleLocator, attribute_name: str):
        return await self._get_locator(locator).get_attribute(attribute_name)

    async def get_input_value(self, locator: FlexibleLocator):
        return await self._get_locator(locator).input_value(timeout=self.default_timeout)

    async def is_visible(self, locator: FlexibleLocator, index: Optional[int] = None,
                         timeout: int = 5000) -> bool:
        """Check visibility, waiting up to ``timeout`` ms for it to appear."""
        try:
            await self._get_locator(locator, index).wait_for(state='visible', timeout=timeout)
            return True
        except Exception:
            return False

    async def is_hidden(self, locator: FlexibleLocator) -> bool:
        return await self._get_locator(locator).is_hidden(timeout=self.default_timeout)

    async def wait_for_element_visible(self, locator: FlexibleLocator, timeout: int = 5000) -> bool:
        try:
            await self._get_locator(locator).wait_for(state='visible', timeout=timeout)
            return True
        except Exception:
            return False

    async def wait_for_element_hidden(self, locator: FlexibleLocator, timeout: int = 5000) -> bool:
        try:
            await self._get_locator(locator).wait_for(state='hidden', timeout=timeout)
            return True
        except Exception:
            return False

    async def wait_for_page_load(self, state: str = 'load'):
        await self.page.wait_for_load_state(state)

    async def get_current_url(self) -> str:
        return self.page.url

    async def accept_next_dialog(self):
        self.page.once('dialog', lambda dialog: dialog.accept())

    async def dismiss_next_dialog(self):
        self.page.once('dialog', lambda dialog: dialog.dismiss())

    async def sleep(self, timeout: int):
        await self.page.wait_for_timeout(timeout)

    async def navigate_to(self, url: str, wait_until: Optional[str] = None):
        await self.page.goto(url, wait_until=wait_until or settings.PAGE_WAIT_UNTIL)

    async def report_log(self, title: str, *args: Any):
        formatted = ', '.join([
            json.dumps(a) if isinstance(a, (dict, list)) else str(a)
            for a in args
        ])
        print(f'{title}: {formatted}' if formatted else title)

    async def goto(self, path: str = '/'):
        base_url = os.getenv('BASE_URL', '')
        url = f'{base_url.rstrip("/")}{path}' if base_url else path
        await self.navigate_to(url)
