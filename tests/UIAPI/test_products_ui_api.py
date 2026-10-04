"""Products catalog, search and brands cross-validated against the real API.

These pages are server-rendered, so there is no AJAX endpoint to mock. The
hybrid UI + API pattern is applied the other way round: the real REST API is
used to seed the expected data, and the UI is asserted to render exactly the
products / brands the API exposes.
"""
from urllib.parse import unquote

import pytest


def _normalise(value: str) -> str:
    return " ".join(value.strip().lower().split())


@pytest.mark.ui_api
class TestProductsUIAPI:
    async def test_ui_products_match_api_products_list(self, ui, api):
        """Every product rendered by the UI exists in the API productsList."""
        await ui.home.open()
        await ui.products.open()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"

        data = await api.products.get_all_products()
        api.products.assert_response(data, 200)
        api_names = {_normalise(p["name"]) for p in data["products"]}
        assert api_names, "API returned no products"

        ui_names = [_normalise(n) for n in await ui.products.get_product_names()]
        assert ui_names, "No products rendered in the UI"

        missing = [n for n in ui_names if n not in api_names]
        assert not missing, f"UI products missing from the API catalog: {missing[:5]}"

    async def test_ui_search_matches_api_search_results(self, ui, api):
        """Searching "tshirt" in the UI shows the same products the API returns."""
        await ui.home.open()
        await ui.products.open()
        await ui.products.search_product("tshirt")
        assert await ui.products.is_searched_products_visible(), "'SEARCHED PRODUCTS' is not visible"

        data = await api.search.search_product("tshirt")
        api.search.assert_response(data, 200)
        api_names = [_normalise(p["name"]) for p in data["products"]]
        assert api_names, "API returned no search results"

        ui_names = [_normalise(n) for n in await ui.products.get_product_names()]
        assert ui_names, "UI returned no search results"

        common = [n for n in api_names if n in ui_names]
        assert common, f"UI results {ui_names[:5]} do not overlap API results {api_names[:5]}"

    async def test_ui_brands_match_api_brands_list(self, ui, api):
        """Every brand rendered in the sidebar exists in the API brandsList."""
        await ui.home.open()
        await ui.products.open()

        data = await api.brands.get_all_brands()
        api.brands.assert_response(data, 200)
        api_brands = {_normalise(b["brand"]) for b in data["brands"]}
        assert api_brands, "API returned no brands"

        links = ui.products.page.locator(".brands-name a")
        assert await links.count() > 0, "No brands rendered in the UI"
        ui_brands = set()
        for i in range(await links.count()):
            href = await links.nth(i).get_attribute("href")
            ui_brands.add(_normalise(unquote(href.rsplit("/", 1)[-1])))

        missing = [b for b in ui_brands if b not in api_brands]
        assert not missing, f"UI brands missing from the API brandsList: {missing}"