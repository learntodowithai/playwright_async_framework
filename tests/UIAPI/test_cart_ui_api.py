"""E2E cart flows: the APIs the UI triggers are mocked and verified.

While using the cart the front-end fires two AJAX calls (cart.js):

  * ``GET /add_to_cart/<product_id>``   - the "Add to cart" buttons
  * ``GET /add_to_cart/<id>?quantity=N`` - the "Add to cart" on product detail
  * ``GET /delete_cart/<product_id>``   - the remove button on the cart page

Each test performs real UI actions, intercepts and mocks those calls, asserts
the exact request the UI sent, and cross-validates the product id against the
real ``productsList`` API.
"""
import pytest


@pytest.mark.ui_api
class TestCartUIAPI:
    async def test_add_to_cart_mocks_api_and_opens_modal(self, ui, api, mock_api):
        """E2E: click "Add to cart" -> the UI calls /add_to_cart/<id> which we mock.

        The mocked success response lets the modal open without touching the
        backend, and the captured request proves the UI hit the right product.
        """
        await mock_api.mock_cart_add()

        await ui.home.open()
        await ui.products.open()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"

        ui_names = await ui.products.get_product_names()
        assert ui_names, "No products rendered on the products page"

        await ui.products.add_product_to_cart(0)
        assert await ui.products.page.locator("#cartModal").is_visible(), "Cart modal did not open"

        request = mock_api.expect_requested("/add_to_cart/", method="GET")
        assert request.path.startswith("/add_to_cart/"), f"Unexpected path {request.path}"
        product_id = request.path.split("/add_to_cart/")[1].rstrip("/")

        products = await api.products.get_all_products()
        api.products.assert_response(products, 200)
        api_by_id = {str(p["id"]): p["name"].strip().lower() for p in products["products"]}
        assert product_id in api_by_id, f"UI sent an unknown product id {product_id}"

        assert ui_names[0].lower() == api_by_id[product_id], (
            f"UI product '{ui_names[0]}' does not match API product '{api_by_id[product_id]}'"
        )

    async def test_add_to_cart_from_product_details_sends_quantity(self, ui, api, mock_api):
        """E2E: quantity + "Add to cart" on the detail page -> /add_to_cart/<id>?quantity=N.

        The mocked response is returned to the UI; the captured query string is
        asserted so the API contract the UI relies on is verified.
        """
        products = await api.products.get_all_products()
        api.products.assert_response(products, 200)
        product_id = products["products"][0]["id"]

        await mock_api.mock_cart_add()

        await ui.product_details.open(product_id)
        await ui.product_details.set_quantity(2)
        await ui.product_details.add_to_cart()
        assert await ui.product_details.page.locator("#cartModal").is_visible(), "Cart modal did not open"

        request = mock_api.expect_requested("/add_to_cart/", method="GET")
        assert request.path == f"/add_to_cart/{product_id}", f"Unexpected path {request.path}"
        assert request.query.get("quantity") == ["2"], (
            f"Expected quantity=2 in the request, got {request.query}"
        )

    async def test_add_to_cart_api_failure_does_not_open_modal(self, ui, mock_api):
        """E2E: when the mocked add_to_cart API returns 500 the modal stays closed."""
        await mock_api.mock_cart_add_failure(status=500)

        await ui.home.open()
        await ui.products.open()

        card = ui.products.page.locator(ui.products.PRODUCT_CARD).nth(0)
        await card.hover()
        await card.locator("a.add-to-cart").first.click()

        request = await mock_api.wait_for_request("/add_to_cart/", method="GET")
        assert request.method == "GET"
        modal = ui.products.page.locator("#cartModal")
        assert await modal.is_hidden(), "Cart modal should not open when the API fails"

    async def test_remove_from_cart_mocks_delete_cart_api(self, ui, mock_api):
        """E2E: removing a product fires /delete_cart/<id>, which is mocked.

        The product is first added through the real backend so the cart page
        renders a row; the removal call is then intercepted and mocked so the
        row is removed purely from the mocked API response.
        """
        await mock_api.capture_cart_add()

        await ui.home.open()
        await ui.home.add_to_cart_from_featured(0)
        assert await ui.home.page.locator("#cartModal").is_visible(), "Cart modal did not open"
        await ui.home.click_view_cart()
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"

        product_names = await ui.cart.get_cart_product_names()
        assert product_names, "Cart is empty, nothing to remove"
        product_name = product_names[0]

        await mock_api.mock_cart_delete()
        await ui.cart.remove_product(product_name)

        request = mock_api.expect_requested("/delete_cart/", method="GET")
        assert request.path.startswith("/delete_cart/"), f"Unexpected path {request.path}"
        assert not await ui.cart.is_product_in_cart(product_name), (
            f"'{product_name}' is still in the cart after removal"
        )