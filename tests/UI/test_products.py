"""Product listing, search, category, brand and review test cases (8, 9, 18, 19, 21)."""
import re

import pytest
from playwright.async_api import expect


@pytest.mark.ui
@pytest.mark.usefixtures("ui")
@pytest.mark.asyncio
class TestProducts:
    async def test_all_products_and_product_detail(self, ui):
        """Test Case 8: Verify All Products and product detail page."""
        await ui.home.open()
        await ui.home.click_products()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"
        assert await ui.products.page.locator(".features_items").is_visible(), "Products list is not visible"

        await ui.products.view_product(0)
        assert "/product_details/" in await ui.product_details.get_current_url(), "Not on product detail page"
        assert await ui.product_details.get_product_name(), "Product name missing"
        assert await ui.product_details.is_detail_complete(), "Product detail is incomplete"

    async def test_search_product(self, ui):
        """Test Case 9: Search Product."""
        await ui.home.open()
        await ui.home.click_products()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"
        await ui.products.search_product("tshirt")
        assert await ui.products.is_searched_products_visible(), "'SEARCHED PRODUCTS' is not visible"
        assert len(await ui.products.get_product_names()) > 0, "No products found for the search"

    async def test_view_category_products(self, ui):
        """Test Case 18: View Category Products."""
        await ui.home.open()
        await ui.products.open()
        await ui.products.click_category("Women", "/category_products/1")
        assert "category_products" in await ui.products.get_current_url(), "Category page not displayed"
        assert "women - dress products" in (await ui.products.get_page_heading()).lower()

        await ui.products.click_category("Men", "/category_products/3")
        assert "category_products" in await ui.products.get_current_url(), "Men category page not displayed"
        assert "men - tshirts products" in (await ui.products.get_page_heading()).lower()

    async def test_view_brand_products(self, ui):
        """Test Case 19: View & Cart Brand Products."""
        await ui.home.open()
        await ui.products.open()
        assert await ui.products.page.locator(".brands-name").is_visible(), "Brands are not visible"

        await ui.products.click_brand("Polo")
        await expect(ui.products.page).to_have_url(re.compile(r"brand_products"))
        await expect(ui.products.page.locator(".features_items")).to_be_visible()

        await ui.products.click_brand("H&M")
        await expect(ui.products.page).to_have_url(re.compile(r"brand_products"))
        await expect(ui.products.page.locator(".features_items")).to_be_visible()

    async def test_add_review_on_product(self, ui):
        """Test Case 21: Add review on product."""
        await ui.home.open()
        await ui.products.open()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"
        await ui.products.view_product(0)
        assert await ui.product_details.is_write_review_visible(), "'Write Your Review' is not visible"
        await ui.product_details.submit_review("QA Tester", "qa@example.com", "Great product, highly recommended!")
        assert await ui.product_details.is_review_success_visible(), "Review success message is not visible"
