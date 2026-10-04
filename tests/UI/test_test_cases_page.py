"""Test Case 7: Verify Test Cases Page."""
import pytest


@pytest.mark.ui
@pytest.mark.smoke
class TestTestCasesPage:
    async def test_verify_test_cases_page(self, ui):
        await ui.home.open()
        assert await ui.home.is_home_page_visible(), "Home page is not visible"
        await ui.home.click_test_cases()
        assert await ui.test_cases.is_test_cases_page_visible(), "Test Cases page is not visible"
