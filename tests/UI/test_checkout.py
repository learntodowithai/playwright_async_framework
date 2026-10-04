"""Checkout / payment / invoice test cases (14, 15, 16, 23, 24)."""
import pytest
from pathlib import Path

from utils.data_generator import payment_details

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"


async def _add_product_and_open_cart(ui) -> None:
    await ui.home.add_to_cart_from_featured(0)
    await ui.home.click_continue_shopping()
    await ui.home.click_cart()


async def _complete_checkout(ui, user: dict) -> None:
    """Address/review verification + comment + place order."""
    assert await ui.checkout.is_checkout_visible(), "Checkout page is not displayed"
    assert await ui.checkout.address_matches(user), "Delivery/Billing address does not match the registered address"
    await ui.checkout.fill_comment("Please deliver between 9am and 5pm.")
    await ui.checkout.click_place_order()


async def _pay_and_confirm(ui) -> None:
    assert await ui.payment.is_payment_page_visible(), "Payment page is not visible"
    await ui.payment.fill_payment_details(payment_details())
    await ui.payment.click_pay_and_confirm()
    assert await ui.order_success.is_order_placed_visible(), "'Your order has been confirmed!' is not visible"


async def _register_via_ui(ui, user: dict) -> None:
    await ui.auth.fill_signup(user["name"], user["email"])
    await ui.auth.click_signup()
    await ui.signup.fill_account_details(user)
    await ui.signup.create_account()
    assert await ui.account.is_account_created_visible(), "'ACCOUNT CREATED!' is not visible"
    await ui.account.click_continue()


@pytest.mark.ui
class TestCheckout:
    async def test_place_order_register_while_checkout(self, ui, new_user):
        """Test Case 14: Place Order: Register while Checkout."""
        await ui.home.open()
        await _add_product_and_open_cart(ui)
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"

        await ui.cart.click_proceed_to_checkout()
        await ui.checkout.click_register_login()
        await _register_via_ui(ui, new_user)
        assert await ui.home.is_logged_in_as(new_user["name"]), "User is not logged in"

        await ui.home.click_cart()
        await ui.cart.click_proceed_to_checkout()
        await _complete_checkout(ui, new_user)
        await _pay_and_confirm(ui)

        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()

    async def test_place_order_register_before_checkout(self, ui, registered_user):
        """Test Case 15: Place Order: Register before Checkout."""
        assert await ui.home.is_logged_in_as(registered_user["name"]), "User is not logged in"
        await _add_product_and_open_cart(ui)
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"

        await ui.cart.click_proceed_to_checkout()
        await _complete_checkout(ui, registered_user)
        await _pay_and_confirm(ui)

        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()

    async def test_place_order_login_before_checkout(self, ui, existing_user):
        """Test Case 16: Place Order: Login before Checkout."""
        await ui.auth.open()
        await ui.auth.fill_login(existing_user["email"], existing_user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(existing_user["name"]), "User is not logged in"

        await _add_product_and_open_cart(ui)
        assert await ui.cart.is_cart_page_visible(), "Cart page is not displayed"

        await ui.cart.click_proceed_to_checkout()
        await _complete_checkout(ui, existing_user)
        await _pay_and_confirm(ui)

        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()

    async def test_verify_address_details_in_checkout(self, ui, registered_user):
        """Test Case 23: Verify address details in checkout page."""
        await _add_product_and_open_cart(ui)
        await ui.cart.click_proceed_to_checkout()
        assert await ui.checkout.is_checkout_visible(), "Checkout page is not displayed"
        assert await ui.checkout.address_matches(registered_user), \
            "Delivery/billing address does not match the registered address"

        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()

    async def test_download_invoice_after_purchase(self, ui, new_user):
        """Test Case 24: Download Invoice after purchase order."""
        await ui.home.open()
        await _add_product_and_open_cart(ui)
        await ui.cart.click_proceed_to_checkout()
        await ui.checkout.click_register_login()
        await _register_via_ui(ui, new_user)
        await ui.home.click_cart()
        await ui.cart.click_proceed_to_checkout()
        await _complete_checkout(ui, new_user)
        await _pay_and_confirm(ui)

        invoice_path = REPORTS_DIR / "invoice.txt"
        await ui.order_success.click_download_invoice(str(invoice_path))
        assert invoice_path.exists(), "Invoice was not downloaded"
        assert invoice_path.stat().st_size > 0, "Downloaded invoice is empty"

        await ui.order_success.click_continue()
        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()
