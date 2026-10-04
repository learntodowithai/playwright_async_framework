"""Test Cases 2-5: Login, logout and sign-up error scenarios."""
import pytest


@pytest.mark.ui
class TestLogin:
    async def test_login_with_correct_credentials(self, ui, existing_user):
        """Test Case 2: Login User with correct email and password."""
        await ui.auth.open()
        assert await ui.auth.is_login_to_account_visible(), "'Login to your account' is not visible"
        await ui.auth.fill_login(existing_user["email"], existing_user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(existing_user["name"]), "Logged in as user is not visible"
        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"

    async def test_login_with_incorrect_credentials(self, ui):
        """Test Case 3: Login User with incorrect email and password."""
        await ui.auth.open()
        assert await ui.auth.is_login_to_account_visible(), "'Login to your account' is not visible"
        await ui.auth.fill_login("wrong@example.com", "wrong-password")
        await ui.auth.click_login()
        assert await ui.auth.is_login_error_visible(), "Incorrect login error is not visible"

    async def test_logout_user(self, ui, registered_user):
        """Test Case 4: Logout User."""
        assert await ui.home.is_logged_in_as(registered_user["name"]), "User should be logged in"
        await ui.home.click_logout()
        assert await ui.auth.is_login_to_account_visible(), "User was not navigated to the login page"

    async def test_register_with_existing_email(self, ui, existing_user):
        """Test Case 5: Register User with existing email."""
        await ui.auth.open()
        await ui.auth.fill_signup(existing_user["name"], existing_user["email"])
        await ui.auth.click_signup()
        assert await ui.auth.is_existing_email_error_visible(), "'Email Address already exist!' is not visible"
