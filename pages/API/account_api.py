"""API endpoints related to user account management."""
from typing import Dict

from pages.API.base_api import BaseAPI


class AccountAPI(BaseAPI):
    CREATE_ACCOUNT_PATH = "/api/createAccount"
    DELETE_ACCOUNT_PATH = "/api/deleteAccount"
    UPDATE_ACCOUNT_PATH = "/api/updateAccount"
    USER_DETAIL_PATH = "/api/getUserDetailByEmail"

    @staticmethod
    def _payload(user: Dict[str, str]) -> Dict[str, str]:
        """Map a test-user dict to the API form fields."""
        return {
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
            "title": user["title"],
            "birth_date": user["birth_date"],
            "birth_month": user["birth_month"],
            "birth_year": user["birth_year"],
            "firstname": user["first_name"],
            "lastname": user["last_name"],
            "company": user["company"],
            "address1": user["address1"],
            "address2": user["address2"],
            "country": user["country"],
            "zipcode": user["zipcode"],
            "state": user["state"],
            "city": user["city"],
            "mobile_number": user["mobile_number"],
        }

    async def create_account(self, user: Dict[str, str]):
        """API 11: POST to create a new user account."""
        response = await self.post(self.CREATE_ACCOUNT_PATH, form=self._payload(user))
        return await self.parse(response)

    async def delete_account(self, email: str, password: str):
        """API 12: DELETE a user account."""
        response = await self.delete(
            self.DELETE_ACCOUNT_PATH, form={"email": email, "password": password}
        )
        return await self.parse(response)

    async def update_account(self, user: Dict[str, str]):
        """API 13: PUT to update a user account."""
        response = await self.put(self.UPDATE_ACCOUNT_PATH, form=self._payload(user))
        return await self.parse(response)

    async def get_user_detail_by_email(self, email: str):
        """API 14: GET user account detail by email."""
        response = await self.get(self.USER_DETAIL_PATH, params={"email": email})
        return await self.parse(response)
