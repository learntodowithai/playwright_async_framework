"""API endpoints related to user login verification."""
from pages.API.base_api import BaseAPI


class LoginAPI(BaseAPI):
    VERIFY_LOGIN_PATH = "/api/verifyLogin"

    async def verify_login(self, email: str, password: str):
        """API 7/10: POST to verify login with email and password."""
        response = await self.post(self.VERIFY_LOGIN_PATH, form={"email": email, "password": password})
        return await self.parse(response)

    async def verify_login_without_email(self, password: str):
        """API 8: POST to verify login without the email parameter."""
        response = await self.post(self.VERIFY_LOGIN_PATH, form={"password": password})
        return await self.parse(response)

    async def verify_login_delete(self, email: str, password: str):
        """API 9: DELETE to verify login (expected to be unsupported)."""
        response = await self.delete(self.VERIFY_LOGIN_PATH, form={"email": email, "password": password})
        return await self.parse(response)
