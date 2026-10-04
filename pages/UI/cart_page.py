"""Page object for the shopping cart page."""
from typing import List

from playwright.async_api import expect

from pages.base_page import BasePage
from pages.UI.components import ScrollMixin, SubscriptionMixin


class CartPage(ScrollMixin, SubscriptionMixin, BasePage):
    SHOPPING_CART_TITLE = "text=Shopping Cart"
    EMPTY_CART_TEXT = "text=Cart is empty!"
    CART_TABLE = "#cart_info_table"
    CART_ROW = "#cart_info_table tbody tr"
    PRODUCT_NAME = ".cart_description h4 a"
    PRODUCT_PRICE = ".cart_price p"
    PRODUCT_QUANTITY = ".cart_quantity button"
    PRODUCT_TOTAL = ".cart_total .cart_total_price"
    DELETE_BUTTON = ".cart_delete a"
    PROCEED_TO_CHECKOUT = "a.check_out"

    async def open(self) -> None:
        await self.goto("/view_cart")

    async def is_cart_page_visible(self) -> bool:
        try:
            await expect(self.page.locator(self.SHOPPING_CART_TITLE)).to_be_visible(timeout=self.default_timeout)
            return True
        except Exception:
            return False

    async def get_cart_item_count(self) -> int:
        return await self.page.locator(self.CART_ROW).count()

    async def get_cart_product_names(self) -> List[str]:
        names = self.page.locator(self.PRODUCT_NAME)
        return [
            " ".join((await names.nth(i).inner_text()).split())
            for i in range(await names.count())
        ]

    async def is_product_in_cart(self, product_name: str) -> bool:
        names = await self.get_cart_product_names()
        needle = " ".join(product_name.split()).lower()
        return needle in [n.lower() for n in names]

    async def get_product_quantity(self, product_name: str) -> int:
        row = self.page.locator(self.CART_ROW).filter(has_text=product_name).first
        await expect(row).to_be_visible()
        return int((await row.locator(self.PRODUCT_QUANTITY).inner_text()).strip())

    async def wait_for_product_quantity(self, product_name: str, quantity: int) -> None:
        """Poll until the product's quantity column shows the expected value."""
        row = self.page.locator(self.CART_ROW).filter(has_text=product_name).first
        await expect(row.locator(self.PRODUCT_QUANTITY)).to_have_text(
            str(quantity), timeout=self.default_timeout
        )

    async def get_product_price(self, product_name: str) -> str:
        row = self.page.locator(self.CART_ROW).filter(has_text=product_name).first
        return (await row.locator(self.PRODUCT_PRICE).inner_text()).strip()

    async def get_product_total(self, product_name: str) -> str:
        row = self.page.locator(self.CART_ROW).filter(has_text=product_name).first
        return (await row.locator(self.PRODUCT_TOTAL).inner_text()).strip()

    async def remove_product(self, product_name: str) -> None:
        row = self.page.locator(self.CART_ROW).filter(has_text=product_name).first
        delete = row.locator(self.DELETE_BUTTON)
        # The site binds the delete handler from cart.js after page scripts load;
        # wait for it so the click actually removes the row.
        await self.page.wait_for_function(
            """() => {
                if (!window.jQuery) return false;
                var a = document.querySelector('.cart_quantity_delete');
                if (!a) return false;
                var ev = jQuery._data(a, 'events');
                return !!(ev && ev.click && ev.click.length);
            }""",
            timeout=self.default_timeout,
        )
        await delete.click()
        await expect(row).not_to_be_attached(timeout=5000)

    async def click_proceed_to_checkout(self) -> None:
        await self.click(self.PROCEED_TO_CHECKOUT, msg="Proceed to checkout")
