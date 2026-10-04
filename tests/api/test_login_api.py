"""API tests 7-10: login verification endpoints."""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.api
class TestLoginAPI:
    async def test_post_verify_login_valid_details(self, api, created_user):
        """API 7: POST To Verify Login with valid details -> 200 'User exists!'."""
        data = await api.login.verify_login(created_user["email"], created_user["password"])
        api.login.assert_response(
            data,
            API_EXPECTED["login_valid_200"]["code"],
            API_EXPECTED["login_valid_200"]["message"],
        )

    async def test_post_verify_login_without_email(self, api):
        """API 8: POST To Verify Login without email parameter -> 400."""
        data = await api.login.verify_login_without_email("somepassword")
        api.login.assert_response(
            data,
            API_EXPECTED["login_missing_param_400"]["code"],
            API_EXPECTED["login_missing_param_400"]["message"],
        )

    async def test_delete_verify_login(self, api):
        """API 9: DELETE To Verify Login -> 405 method not supported."""
        data = await api.login.verify_login_delete("a@b.com", "pw")
        api.login.assert_response(
            data,
            API_EXPECTED["login_delete_405"]["code"],
            API_EXPECTED["login_delete_405"]["message"],
        )

    async def test_post_verify_login_invalid_details(self, api):
        """API 10: POST To Verify Login with invalid details -> 404 'User not found!'."""
        data = await api.login.verify_login("nonexistent@example.com", "wrong-password")
        api.login.assert_response(
            data,
            API_EXPECTED["login_invalid_404"]["code"],
            API_EXPECTED["login_invalid_404"]["message"],
        )
