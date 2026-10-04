"""Registration E2E flow: the UI creates the account, the API verifies it.

The sign-up forms on automationexercise.com are server-rendered HTML form
POSTs, so there is no AJAX call to mock. The hybrid UI + API pattern here is:

1. **Precondition (API)** - ``getUserDetailByEmail`` confirms the email is not
   registered yet (responseCode 404).
2. **UI action (E2E)** - the full registration journey is driven through the
   browser: sign-up form, account information form, "ACCOUNT CREATED!".
3. **Postcondition (API)** - ``getUserDetailByEmail`` now returns the account
   with matching email and name, proving the UI action persisted through the
   API-backed backend.
4. **Cleanup (API)** - ``deleteAccount`` removes the account.
"""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.ui_api
class TestRegisterUIAPI:
    async def test_register_via_ui_verify_via_api(self, ui, api, new_user):
        user = new_user

        # Precondition: the email must be free at the API layer.
        missing = await api.account.get_user_detail_by_email(user["email"])
        assert api.account.response_code(missing) == 404, (
            f"Account with {user['email']} already exists: {missing}"
        )

        # UI journey: sign-up -> account information -> account created.
        await ui.auth.open()
        assert await ui.auth.is_new_user_signup_visible(), "'New User Signup!' is not visible"
        await ui.auth.fill_signup(user["name"], user["email"])
        await ui.auth.click_signup()
        assert await ui.signup.is_enter_account_info_visible(), (
            "'ENTER ACCOUNT INFORMATION' is not visible"
        )
        await ui.signup.fill_account_details(user)
        await ui.signup.create_account()
        assert await ui.account.is_account_created_visible(), "'ACCOUNT CREATED!' is not visible"
        await ui.account.click_continue()
        assert await ui.home.is_logged_in_as(user["name"]), "User is not logged in"

        # Postcondition: the account now exists at the API layer with matching detail.
        detail = await api.account.get_user_detail_by_email(user["email"])
        api.account.assert_response(detail, API_EXPECTED["products_get"]["code"])
        assert detail.get("user"), "API returned no user detail"
        assert detail["user"]["email"] == user["email"], "API user email does not match"
        assert detail["user"]["name"] == user["name"], "API user name does not match"

        # Cleanup: delete the account through the API.
        deleted = await api.account.delete_account(user["email"], user["password"])
        api.account.assert_response(
            deleted,
            API_EXPECTED["delete_account_200"]["code"],
            API_EXPECTED["delete_account_200"]["message"],
        )