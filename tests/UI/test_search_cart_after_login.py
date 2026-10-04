"""Test Case 20: Search Products and Verify Cart After Login."""
import pytest


@pytest.mark.ui
class TestSearchAndCartAfterLogin:
    async def test_search_products_and_verify_cart_after_login(self, ui, existing_user):
        await ui.home.open()
        await ui.products.open()
        assert await ui.products.is_all_products_visible(), "ALL PRODUCTS page is not visible"

        await ui.products.search_product("tshirt")
        assert await ui.products.is_searched_products_visible(), "'SEARCHED PRODUCTS' is not visible"
        names = (await ui.products.get_product_names())[:2]

        await ui.products.add_product_to_cart(0)
        await ui.products.click_continue_shopping()
        await ui.products.add_product_to_cart(1)
        await ui.products.click_view_cart()
        for name in names:
            assert await ui.cart.is_product_in_cart(name), f"{name} is not visible in the cart"

        await ui.home.click_signup_login()
        await ui.auth.fill_login(existing_user["email"], existing_user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(existing_user["name"]), "User is not logged in"

        await ui.home.click_cart()
        for name in names:
            assert await ui.cart.is_product_in_cart(name), f"{name} is not visible in the cart after login"
