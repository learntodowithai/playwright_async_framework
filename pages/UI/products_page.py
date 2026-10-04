"""Page object for the Products / ALL PRODUCTS listing page."""
from typing import List

from playwright.async_api import expect

from pages.base_page import BasePage


class ProductsPage(BasePage):
    ALL_PRODUCTS_TITLE = "text=ALL PRODUCTS"
    SEARCHED_PRODUCTS_TITLE = "text=SEARCHED PRODUCTS"
    SEARCH_INPUT = "#search_product"
    SEARCH_BUTTON = "#submit_search"
    PRODUCT_CARD = ".features_items .product-image-wrapper"
    PRODUCT_NAME_IN_CARD = ".productinfo p"
    VIEW_PRODUCT_LINK = 'a[href^="/product_details/"]'
    BRAND_LINK = ".brands-name a"
    PAGE_HEADING = "h2.title.text-center"

    # Add-to-cart modal
    CART_MODAL = "#cartModal"
    CART_MODAL_TITLE = "#cartModal .modal-title"
    MODAL_VIEW_CART_LINK = '#cartModal a[href="/view_cart"]'
    MODAL_CONTINUE_SHOPPING = "#cartModal .close-modal"

    async def open(self) -> None:
        await self.goto("/products")

    async def is_all_products_visible(self) -> bool:
        return await self.is_visible(self.ALL_PRODUCTS_TITLE)

    async def is_searched_products_visible(self) -> bool:
        return await self.is_visible(self.SEARCHED_PRODUCTS_TITLE)

    async def search_product(self, product_name: str) -> None:
        await self.fill(self.SEARCH_INPUT, product_name, msg=f"Search for {product_name}")
        await self.click(self.SEARCH_BUTTON, msg="Click search")

    async def get_product_names(self) -> List[str]:
        names = self.page.locator(self.PRODUCT_CARD)
        result = []
        for i in range(await names.count()):
            text = await names.nth(i).locator(self.PRODUCT_NAME_IN_CARD).inner_text()
            result.append(" ".join(text.split()))
        return result

    async def view_product(self, index: int = 0) -> None:
        card = self.page.locator(self.PRODUCT_CARD).nth(index)
        await card.locator(self.VIEW_PRODUCT_LINK).click()

    async def add_product_to_cart(self, index: int = 0) -> None:
        card = self.page.locator(self.PRODUCT_CARD).nth(index)
        await card.hover()
        await card.locator("a.add-to-cart").first.click()
        await self._get_locator(self.CART_MODAL_TITLE).wait_for(state="visible", timeout=8000)

    async def click_view_cart(self) -> None:
        await self.click(self.MODAL_VIEW_CART_LINK, msg="View Cart from modal")

    async def click_continue_shopping(self) -> None:
        await self.click(self.MODAL_CONTINUE_SHOPPING, msg="Continue Shopping")
        await self.wait_for_element_hidden(self.CART_MODAL, timeout=5000)

    async def click_brand(self, brand_name: str) -> None:
        await self.click(self.page.locator(self.BRAND_LINK, has_text=brand_name), msg=f"Select brand {brand_name}")

    async def get_page_heading(self) -> str:
        return (await self.page.locator(self.PAGE_HEADING).first.inner_text()).strip()

    async def click_category(self, category: str, sub_href: str) -> None:
        """Expand a top-level category and click one of its sub-categories."""
        await self.click(f'#accordian a[href="#{category}"]', msg=f"Expand {category} category")
        await self.click(f'#{category} a[href="{sub_href}"]', msg=f"Select {category} sub-category")

