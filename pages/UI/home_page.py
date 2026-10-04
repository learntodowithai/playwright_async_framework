"""Page object for the Automation Exercise home page and shared header/footer."""
from typing import List

from playwright.async_api import expect

from pages.base_page import BasePage
from pages.UI.components import ScrollMixin, SubscriptionMixin


class HomePage(SubscriptionMixin, ScrollMixin, BasePage):
    # ---- Header navigation ----
    SIGNUP_LOGIN_LINK = 'a[href="/login"]'
    PRODUCTS_LINK = 'a[href="/products"]'
    CART_LINK = 'a[href="/view_cart"]'
    TEST_CASES_LINK = 'a[href="/test_cases"]'
    CONTACT_US_LINK = 'a[href="/contact_us"]'
    LOGOUT_LINK = 'a[href="/logout"]'
    DELETE_ACCOUNT_LINK = 'a[href="/delete_account"]'
    LOGGED_IN_AS = "//li/a[contains(., 'Logged in as')]"

    # ---- Main content ----
    SLIDER_CAROUSEL = "#slider-carousel"
    FEATURED_ITEMS = ".features_items"
    PRODUCT_CARD = ".features_items .product-image-wrapper"
    VIEW_PRODUCT_LINK = 'a[href^="/product_details/"]'

    # ---- Left sidebar ----
    WOMEN_CATEGORY = '#accordian a[href="#Women"]'
    WOMEN_DRESS_LINK = '#Women a[href="/category_products/1"]'
    MEN_TSHIRTS_LINK = '#Men a[href="/category_products/3"]'
    BRAND_LINK = ".brands-name a"

    # ---- Add-to-cart modal ----
    CART_MODAL = "#cartModal"
    MODAL_TITLE = "#cartModal .modal-title"
    MODAL_VIEW_CART_LINK = '#cartModal a[href="/view_cart"]'
    MODAL_CONTINUE_SHOPPING = "#cartModal .close-modal"

    # ---- Recommended items ----
    RECOMMENDED_ITEMS = ".recommended_items"
    RECOMMENDED_PRODUCT_CARD = ".recommended_items .product-image-wrapper"

    async def open(self) -> None:
        await self.goto("/")

    async def is_home_page_visible(self) -> bool:
        return await self.is_visible(self.SLIDER_CAROUSEL)

    # ---- Header actions ----
    async def click_signup_login(self) -> None:
        await self.click(self.SIGNUP_LOGIN_LINK, msg="Open Signup / Login page")

    async def click_products(self) -> None:
        await self.click(self.PRODUCTS_LINK, msg="Open Products page")

    async def click_cart(self) -> None:
        await self.click(self.CART_LINK, msg="Open Cart page")

    async def click_test_cases(self) -> None:
        await self.click(self.TEST_CASES_LINK, msg="Open Test Cases page")

    async def click_contact_us(self) -> None:
        await self.click(self.CONTACT_US_LINK, msg="Open Contact Us page")

    async def click_logout(self) -> None:
        await self.click(self.LOGOUT_LINK, msg="Logout")

    async def click_delete_account(self) -> None:
        await self.click(self.DELETE_ACCOUNT_LINK, msg="Delete account")

    async def is_logged_in_as(self, username: str) -> bool:
        locator = self.page.locator(self.LOGGED_IN_AS)
        await expect(locator).to_contain_text("Logged in as", timeout=self.default_timeout)
        text = await locator.inner_text()
        return username.lower() in text.lower()

    # ---- Featured products ----
    async def click_first_view_product(self) -> None:
        card = self.page.locator(self.PRODUCT_CARD).nth(0)
        await card.locator(self.VIEW_PRODUCT_LINK).click()

    async def add_to_cart_from_featured(self, index: int = 0) -> None:
        card = self.page.locator(self.PRODUCT_CARD).nth(index)
        await card.hover()
        await card.locator("a.add-to-cart").first.click()
        await self._get_locator(self.MODAL_TITLE).wait_for(state="visible", timeout=8000)

    async def click_continue_shopping(self) -> None:
        await self.click(self.MODAL_CONTINUE_SHOPPING, msg="Continue Shopping")
        await self.wait_for_element_hidden(self.CART_MODAL, timeout=5000)

    async def click_view_cart(self) -> None:
        await self.click(self.MODAL_VIEW_CART_LINK, msg="View Cart from modal")

    # ---- Recommended items ----
    async def is_recommended_items_visible(self) -> bool:
        return await self.is_visible(self.RECOMMENDED_ITEMS)

    async def add_to_cart_from_recommended(self, index: int = 0) -> None:
        await self.scroll_to_bottom()
        card = self.page.locator(self.RECOMMENDED_PRODUCT_CARD).nth(index)
        await card.scroll_into_view_if_needed()
        await card.hover()
        await card.locator("a.add-to-cart").first.click()
        await self._get_locator(self.MODAL_TITLE).wait_for(state="visible", timeout=8000)

    # ---- Categories & brands ----
    async def click_women_dress_category(self) -> None:
        await self.click(self.WOMEN_CATEGORY, msg="Expand Women category")
        await self.click(self.WOMEN_DRESS_LINK, msg="Select Women > Dress")

    async def click_men_tshirts_category(self) -> None:
        await self.click(self.MEN_TSHIRTS_LINK, msg="Select Men > Tshirts")

    async def get_brand_names(self) -> List[str]:
        links = self.page.locator(self.BRAND_LINK)
        return [await links.nth(i).inner_text() for i in range(await links.count())]

    async def click_brand(self, brand_name: str) -> None:
        await self.click(self.page.locator(self.BRAND_LINK, has_text=brand_name), msg=f"Select brand {brand_name}")
