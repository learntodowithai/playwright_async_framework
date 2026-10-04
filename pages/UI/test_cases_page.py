"""Page object for the Test Cases page."""
from playwright.async_api import expect

from pages.base_page import BasePage


class TestCasesPage(BasePage):
    TEST_CASES_TITLE = "h2.text-center"
    TEST_CASE_ITEM = "text=Test Case 1: Register User"

    async def open(self) -> None:
        await self.goto("/test_cases")

    async def is_test_cases_page_visible(self) -> bool:
        title_ok = await self.is_visible(self.TEST_CASES_TITLE)
        url_ok = "/test_cases" in await self.get_current_url()
        return title_ok and url_ok
