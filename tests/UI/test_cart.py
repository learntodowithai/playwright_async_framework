"""Cart related test cases (11, 12, 13, 17, 22)."""
import pytest
from utils.data_generator import unique_email


@pytest.mark.ui
class TestCart:
    async def test_add_products_in_cart(self, ui):
        """Test Case 12: Add Products in Cart."""
        await ui.home.open()
        await ui.products.open()
        names = (await ui.products.get_product_names())[:2]

        await ui.products.add_product_to_cart(0)
        await ui.products.click_continue_shopping()
        await ui.products.add_product_to_cart(1)
        await ui.products.click_view_cart()

        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"
        for name in names:
            assert await ui.cart.is_product_in_cart(name), f"{name} not added to the cart"
            assert await ui.cart.get_product_quantity(name) == 1, f"{name} quantity is not 1"
            assert await ui.cart.get_product_price(name) == await ui.cart.get_product_total(name), \
                f"{name} total price does not match its price"

    async def test_product_quantity_in_cart(self, ui):
        """Test Case 13: Verify Product quantity in Cart."""
        await ui.home.open()
        await ui.home.click_first_view_product()
        product_name = await ui.product_details.get_product_name()
        await ui.product_details.set_quantity(4)
        await ui.product_details.add_to_cart()
        await ui.product_details.click_view_cart()
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"
        await ui.cart.wait_for_product_quantity(product_name, 4)

    async def test_remove_products_from_cart(self, ui):
        """Test Case 17: Remove Products From Cart."""
        await ui.home.open()
        await ui.products.open()
        names = (await ui.products.get_product_names())[:2]
        await ui.products.add_product_to_cart(0)
        await ui.products.click_continue_shopping()
        await ui.products.add_product_to_cart(1)
        await ui.products.click_view_cart()

        await ui.cart.remove_product(names[0])
        assert not await ui.cart.is_product_in_cart(names[0]), f"{names[0]} was not removed from the cart"
        assert await ui.cart.is_product_in_cart(names[1]), f"{names[1]} should still be in the cart"

    async def test_add_to_cart_from_recommended_items(self, ui):
        """Test Case 22: Add to cart from Recommended items."""
        await ui.home.open()
        assert await ui.home.is_recommended_items_visible(), "'RECOMMENDED ITEMS' are not visible"
        await ui.home.add_to_cart_from_recommended(0)
        await ui.home.click_view_cart()
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"
        assert await ui.cart.get_cart_item_count() > 0, "No product displayed in the cart"

    async def test_subscription_in_cart_page(self, ui):
        """Test Case 11: Verify Subscription in Cart page."""
        await ui.home.open()
        await ui.cart.open()
        assert await ui.cart.is_subscription_visible(), "'SUBSCRIPTION' is not visible"
        await ui.cart.subscribe(unique_email())
        assert await ui.cart.is_subscription_success_visible(), "Subscription success message is not visible"
