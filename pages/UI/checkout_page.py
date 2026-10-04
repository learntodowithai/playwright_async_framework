"""Page object for the checkout page (address details + review order)."""
from playwright.async_api import expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    DELIVERY_ADDRESS = "#address_delivery"
    BILLING_ADDRESS = "#address_invoice"
    REVIEW_ORDER_TABLE = "#cart_info"
    COMMENT_TEXTAREA = '#ordermsg textarea[name="message"]'
    PLACE_ORDER_BUTTON = 'a[href="/payment"]'

    async def is_checkout_visible(self) -> bool:
        return await self.is_visible(self.REVIEW_ORDER_TABLE)

    async def get_delivery_address_text(self) -> str:
        return (await self.get_inner_text(self.DELIVERY_ADDRESS)).lower()

    async def get_billing_address_text(self) -> str:
        return (await self.get_inner_text(self.BILLING_ADDRESS)).lower()

    async def address_matches(self, user: dict) -> bool:
        delivery = await self.get_delivery_address_text()
        billing = await self.get_billing_address_text()
        expected = [
            f"{user['first_name']} {user['last_name']}".lower(),
            user["address1"].lower(),
            user["address2"].lower(),
            user["city"].lower(),
            user["state"].lower(),
            user["zipcode"].lower(),
            user["country"].lower(),
            user["mobile_number"].lower(),
        ]
        return all(item in delivery and item in billing for item in expected)

    async def fill_comment(self, comment: str) -> None:
        await self.fill(self.COMMENT_TEXTAREA, comment, msg="Enter order comment")

    async def click_place_order(self) -> None:
        await self.click(self.PLACE_ORDER_BUTTON, msg="Place order")

    async def click_register_login(self) -> None:
        """Proceed from the 'register/login required' checkout modal to the login page."""
        modal = self.page.locator("#checkoutModal")
        try:
            await modal.wait_for(state="visible", timeout=4000)
            await self.click(modal.locator('a[href="/login"]').first, msg="Register / Login from checkout modal")
        except Exception:
            await self.page.goto("/login")
