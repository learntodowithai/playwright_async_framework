"""Page object for the product detail page."""
from typing import List

from playwright.async_api import expect

from pages.base_page import BasePage


class ProductDetailsPage(BasePage):
    PRODUCT_NAME = ".product-information h2"
    PRODUCT_DETAILS = ".product-information p"
    PRODUCT_PRICE = ".product-information span span"
    QUANTITY_INPUT = "#quantity"
    ADD_TO_CART_BUTTON = ".product-information button.btn.btn-default.cart"

    WRITE_REVIEW_TITLE = "text=Write Your Review"
    REVIEW_NAME_INPUT = "#name"
    REVIEW_EMAIL_INPUT = "#email"
    REVIEW_TEXT_INPUT = "#review"
    REVIEW_SUBMIT_BUTTON = "#button-review"
    REVIEW_SUCCESS = "text=Thank you for your review."

    async def open(self, product_id: int) -> None:
        await self.goto(f"/product_details/{product_id}")

    async def get_product_name(self) -> str:
        return (await self.get_inner_text(self.PRODUCT_NAME)).strip()

    async def get_product_price(self) -> str:
        return (await self.get_inner_text(self.PRODUCT_PRICE)).strip()

    async def get_product_details(self) -> List[str]:
        locator = self.page.locator(self.PRODUCT_DETAILS)
        return [ (await locator.nth(i).inner_text()).strip() for i in range(await locator.count()) ]

    async def is_detail_complete(self) -> bool:
        details = " ".join(await self.get_product_details()).lower()
        return ("category:" in details and "availability:" in details
                and "condition:" in details and "brand:" in details)

    async def set_quantity(self, quantity: int) -> None:
        await self.fill(self.QUANTITY_INPUT, str(quantity), msg=f"Set quantity to {quantity}")

    async def add_to_cart(self) -> None:
        await self.click(self.ADD_TO_CART_BUTTON, msg="Add product to cart")
        await self.wait_for_element_visible("#cartModal .modal-title", timeout=5000)

    async def click_view_cart(self) -> None:
        await self.click('#cartModal a[href="/view_cart"]', msg="View Cart from modal")

    async def is_write_review_visible(self) -> bool:
        return await self.is_visible(self.WRITE_REVIEW_TITLE)

    async def submit_review(self, name: str, email: str, review: str) -> None:
        await self.fill(self.REVIEW_NAME_INPUT, name, msg="Enter review name")
        await self.fill(self.REVIEW_EMAIL_INPUT, email, msg="Enter review email")
        await self.fill(self.REVIEW_TEXT_INPUT, review, msg="Enter review text")
        await self.click(self.REVIEW_SUBMIT_BUTTON, msg="Submit review")

    async def is_review_success_visible(self) -> bool:
        return await self.is_visible(self.REVIEW_SUCCESS)
