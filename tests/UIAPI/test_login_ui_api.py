"""Login E2E flows combining the real REST API with UI actions.

The login form on automationexercise.com is a classic HTML form POST to
``/login`` (no AJAX), so the hybrid pattern here is:

1. The **API** creates the user account (precondition) and verifies the
   credentials afterwards (``/api/verifyLogin``).
2. The **UI** performs the real login with those credentials.
3. The login form POST is **captured** mid-flight and its payload is asserted
   to carry exactly the credentials the API validated.
"""
from urllib.parse import parse_qs

import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.ui_api
class TestLoginUIAPI:
    async def test_ui_login_for_api_created_user(self, ui, api, api_created_user):
        """Account seeded via API -> UI login -> API confirms credentials valid."""
        user = api_created_user

        await ui.auth.open()
        assert await ui.auth.is_login_to_account_visible(), "'Login to your account' is not visible"
        await ui.auth.fill_login(user["email"], user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(user["name"]), "User is not logged in after UI login"

        data = await api.login.verify_login(user["email"], user["password"])
        api.login.assert_response(
            data,
            API_EXPECTED["login_valid_200"]["code"],
            API_EXPECTED["login_valid_200"]["message"],
        )

    async def test_ui_login_payload_matches_api_credentials(self, ui, api, api_created_user, mock_api):
        """Capture the login form POST the UI performs and validate its payload."""
        user = api_created_user
        await mock_api.capture("**/login", method="POST")

        await ui.auth.open()
        await ui.auth.fill_login(user["email"], user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(user["name"]), "User is not logged in"

        request = mock_api.expect_requested("/login", method="POST")
        form = parse_qs(request.post_data or "")
        assert user["email"] in form.get("email", []), f"Email not sent in login payload: {form}"
        assert user["password"] in form.get("password", []), (
            f"Password not sent in login payload: {form}"
        )

        data = await api.login.verify_login(user["email"], user["password"])
        api.login.assert_response(
            data,
            API_EXPECTED["login_valid_200"]["code"],
            API_EXPECTED["login_valid_200"]["message"],
        )