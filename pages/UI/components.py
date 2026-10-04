"""Reusable UI components shared across pages (e.g. footer subscription)."""
from pages.base_page import BasePage


class SubscriptionMixin:
    """Footer subscription widget shared by most pages."""

    SUBSCRIPTION_TITLE = "text=Subscription"
    SUBSCRIPTION_EMAIL_INPUT = "#susbscribe_email"
    SUBSCRIPTION_BUTTON = "#subscribe"
    SUBSCRIPTION_SUCCESS = "text=You have been successfully subscribed!"

    async def is_subscription_visible(self) -> bool:
        await self.scroll_to_footer()
        return await self.is_visible(self.SUBSCRIPTION_TITLE)

    async def subscribe(self, email: str) -> None:
        await self.scroll_to_footer()
        await self.fill(self.SUBSCRIPTION_EMAIL_INPUT, email, msg="Enter subscription email")
        await self.click(self.SUBSCRIPTION_BUTTON, msg="Click subscribe")

    async def is_subscription_success_visible(self) -> bool:
        return await self.is_visible(self.SUBSCRIPTION_SUCCESS)


class ScrollMixin:
    """Scrolling helpers."""

    SCROLL_UP_ARROW = "a#scrollUp"
    FULL_FLEDGED_TEXT = "text=Full-Fledged practice website for Automation Engineers"

    async def scroll_to_footer(self) -> None:
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self.page.wait_for_timeout(200)

    async def scroll_to_bottom(self) -> None:
        await self.scroll_to_footer()

    async def scroll_to_top(self) -> None:
        await self.page.evaluate("window.scrollTo(0, 0)")
        await self.page.wait_for_timeout(200)

    async def click_scroll_up_arrow(self) -> None:
        await self.click(self.SCROLL_UP_ARROW, msg="Click scroll-up arrow")

    async def is_full_fledged_text_visible(self) -> bool:
        await self.page.wait_for_timeout(200)
        return await self.is_visible(self.FULL_FLEDGED_TEXT)
