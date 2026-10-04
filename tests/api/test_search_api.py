"""API tests 5-6: product search endpoints."""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.api
class TestSearchAPI:
    async def test_post_to_search_product(self, api):
        """API 5: POST To Search Product -> 200 with matching products."""
        data = await api.search.search_product("tshirt")
        api.search.assert_response(data, API_EXPECTED["products_get"]["code"])
        assert data.get("products"), "No products returned for the search"
        assert any("tshirt" in p.get("name", "").lower() for p in data["products"]), \
            "Searched products do not match the query"

    async def test_post_to_search_product_without_param(self, api):
        """API 6: POST To Search Product without parameter -> 400."""
        data = await api.search.search_product_without_param()
        api.search.assert_response(
            data,
            API_EXPECTED["search_400"]["code"],
            API_EXPECTED["search_400"]["message"],
        )
