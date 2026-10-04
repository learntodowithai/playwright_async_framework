"""API tests 1-2: products list endpoints."""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.api
class TestProductsAPI:
    async def test_get_all_products_list(self, api):
        """API 1: GET All Products List -> 200 with a non-empty list."""
        data = await api.products.get_all_products()
        api.products.assert_response(data, API_EXPECTED["products_get"]["code"])
        assert data.get("products"), "Products list is empty"
        assert data["products"][0].get("name"), "Product payload is missing name"

    async def test_post_all_products_list(self, api):
        """API 2: POST To All Products List -> 405 method not supported."""
        data = await api.products.post_all_products()
        api.products.assert_response(
            data,
            API_EXPECTED["products_post_405"]["code"],
            API_EXPECTED["products_post_405"]["message"],
        )
