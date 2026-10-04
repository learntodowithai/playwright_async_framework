"""API tests 11-14: account management endpoints."""
import pytest
from test_data.user_data import API_EXPECTED


@pytest.mark.api
class TestAccountAPI:
    async def test_post_to_create_account(self, api, created_user):
        """API 11: POST To Create/Register User Account -> 201 'User created!'."""
        # Account creation + assertion already happen in the created_user fixture.

    async def test_delete_method_to_delete_account(self, api, new_user):
        """API 12: DELETE METHOD To Delete User Account -> 200 'Account deleted!'."""
        data = await api.account.create_account(new_user)
        api.account.assert_response(data, API_EXPECTED["create_account_201"]["code"])
        data = await api.account.delete_account(new_user["email"], new_user["password"])
        api.account.assert_response(
            data,
            API_EXPECTED["delete_account_200"]["code"],
            API_EXPECTED["delete_account_200"]["message"],
        )

    async def test_put_method_to_update_account(self, api, created_user):
        """API 13: PUT METHOD To Update User Account -> 200 'User updated!'."""
        updated = dict(created_user)
        updated["company"] = "Updated Corp"
        updated["city"] = "Los Angeles"
        data = await api.account.update_account(updated)
        api.account.assert_response(
            data,
            API_EXPECTED["update_account_200"]["code"],
            API_EXPECTED["update_account_200"]["message"],
        )

    async def test_get_user_account_detail_by_email(self, api, created_user):
        """API 14: GET user account detail by email -> 200 with matching detail."""
        data = await api.account.get_user_detail_by_email(created_user["email"])
        api.account.assert_response(data, API_EXPECTED["products_get"]["code"])
        assert data.get("user"), "User detail is missing from the response"
        assert data["user"].get("email") == created_user["email"], "User detail email does not match"
