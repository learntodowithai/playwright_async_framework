"""Test Case 1: Register User."""
import pytest


@pytest.mark.ui
@pytest.mark.smoke
class TestRegisterUser:
    async def test_register_user(self, ui, new_user):
        # 1-3: Launch browser, navigate, verify home page
        await ui.home.open()
        assert await ui.home.is_home_page_visible(), "Home page is not visible"

        # 4-5: Signup / Login and 'New User Signup!'
        await ui.home.click_signup_login()
        assert await ui.auth.is_new_user_signup_visible(), "'New User Signup!' is not visible"

        # 6-7: Enter name, email and signup
        await ui.auth.fill_signup(new_user["name"], new_user["email"])
        await ui.auth.click_signup()

        # 8: Verify 'ENTER ACCOUNT INFORMATION'
        assert await ui.signup.is_enter_account_info_visible(), "'ENTER ACCOUNT INFORMATION' is not visible"

        # 9-13: Fill details and create account
        await ui.signup.fill_account_details(new_user)
        await ui.signup.create_account()

        # 14-16: Verify account created, continue, logged in
        assert await ui.account.is_account_created_visible(), "'ACCOUNT CREATED!' is not visible"
        await ui.account.click_continue()
        assert await ui.home.is_logged_in_as(new_user["name"]), "Logged in as user is not visible"

        # 17-18: Delete account and verify deletion
        await ui.home.click_delete_account()
        assert await ui.account.is_account_deleted_visible(), "'ACCOUNT DELETED!' is not visible"
        await ui.account.click_continue()
