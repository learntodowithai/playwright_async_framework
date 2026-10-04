"""API tests 3-4: brands list endpoints."""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.api
class TestBrandsAPI:
    async def test_get_all_brands_list(self, api):
        """API 3: GET All Brands List -> 200 with a non-empty list."""
        data = await api.brands.get_all_brands()
        api.brands.assert_response(data, API_EXPECTED["brands_get"]["code"])
        assert data.get("brands"), "Brands list is empty"

    async def test_put_all_brands_list(self, api):
        """API 4: PUT To All Brands List -> 405 method not supported."""
        data = await api.brands.put_all_brands()
        api.brands.assert_response(
            data,
            API_EXPECTED["brands_put_405"]["code"],
            API_EXPECTED["brands_put_405"]["message"],
        )
