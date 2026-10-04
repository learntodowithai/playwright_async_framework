"""Data-driven API tests: users loaded from a CSV file."""
import os

import pytest

from test_data.user_data import API_EXPECTED
from utils.data_generator import unique_email
from utils.data_providers import CsvDataProvider, rows_as_parametrize

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "data")
USERS_CSV = os.path.abspath(os.path.join(DATA_DIR, "users.csv"))

_users, _user_ids = rows_as_parametrize(CsvDataProvider.read_rows(USERS_CSV), id_key="email")


@pytest.mark.api
@pytest.mark.parametrize("user_data", _users, ids=_user_ids)
class TestDataDrivenAPI:
    async def test_csv_driven_create_login_delete_account(self, api, user_data):
        """Create an account from CSV data, verify login, then delete it."""
        user = dict(user_data)
        user["email"] = unique_email()

        created = await api.account.create_account(user)
        api.account.assert_response(
            created,
            API_EXPECTED["create_account_201"]["code"],
            API_EXPECTED["create_account_201"]["message"],
        )

        login = await api.login.verify_login(user["email"], user["password"])
        api.login.assert_response(
            login,
            API_EXPECTED["login_valid_200"]["code"],
            API_EXPECTED["login_valid_200"]["message"],
        )

        deleted = await api.account.delete_account(user["email"], user["password"])
        api.account.assert_response(
            deleted,
            API_EXPECTED["delete_account_200"]["code"],
            API_EXPECTED["delete_account_200"]["message"],
        )
