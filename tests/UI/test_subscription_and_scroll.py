"""Home subscription and scroll test cases (10, 25, 26)."""
import pytest
from utils.data_generator import unique_email


@pytest.mark.ui
class TestSubscriptionAndScroll:
    async def test_subscription_in_home_page(self, ui):
        """Test Case 10: Verify Subscription in home page."""
        await ui.home.open()
        assert await ui.home.is_subscription_visible(), "'SUBSCRIPTION' is not visible"
        await ui.home.subscribe(unique_email())
        assert await ui.home.is_subscription_success_visible(), "Subscription success message is not visible"

    async def test_scroll_up_using_arrow(self, ui):
        """Test Case 25: Verify Scroll Up using 'Arrow' button and Scroll Down functionality."""
        await ui.home.open()
        assert await ui.home.is_home_page_visible(), "Home page is not visible"
        await ui.home.scroll_to_bottom()
        assert await ui.home.is_subscription_visible(), "'SUBSCRIPTION' is not visible"
        await ui.home.click_scroll_up_arrow()
        assert await ui.home.is_full_fledged_text_visible(), "Page did not scroll back up to the top"

    async def test_scroll_up_without_arrow(self, ui):
        """Test Case 26: Verify Scroll Up without 'Arrow' button and Scroll Down functionality."""
        await ui.home.open()
        assert await ui.home.is_home_page_visible(), "Home page is not visible"
        await ui.home.scroll_to_bottom()
        assert await ui.home.is_subscription_visible(), "'SUBSCRIPTION' is not visible"
        await ui.home.scroll_to_top()
        assert await ui.home.is_full_fledged_text_visible(), "Page did not scroll back up to the top"
