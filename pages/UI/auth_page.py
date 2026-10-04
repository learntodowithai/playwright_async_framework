"""Page object for the Signup / Login page."""
from playwright.async_api import expect

from pages.base_page import BasePage


class AuthPage(BasePage):
    # ---- Signup form ----
    SIGNUP_NAME_INPUT = 'input[data-qa="signup-name"]'
    SIGNUP_EMAIL_INPUT = 'input[data-qa="signup-email"]'
    SIGNUP_BUTTON = 'button[data-qa="signup-button"]'
    NEW_USER_SIGNUP_TITLE = "text=New User Signup!"
    EXISTING_EMAIL_ERROR = "text=Email Address already exist!"

    # ---- Login form ----
    LOGIN_EMAIL_INPUT = 'input[data-qa="login-email"]'
    LOGIN_PASSWORD_INPUT = 'input[data-qa="login-password"]'
    LOGIN_BUTTON = 'button[data-qa="login-button"]'
    LOGIN_TO_ACCOUNT_TITLE = "text=Login to your account"
    LOGIN_ERROR = "text=Your email or password is incorrect!"

    async def open(self) -> None:
        await self.goto("/login")

    # ---- Signup ----
    async def is_new_user_signup_visible(self) -> bool:
        return await self.is_visible(self.NEW_USER_SIGNUP_TITLE)

    async def fill_signup(self, name: str, email: str) -> None:
        await self.fill(self.SIGNUP_NAME_INPUT, name, msg="Enter signup name")
        await self.fill(self.SIGNUP_EMAIL_INPUT, email, msg="Enter signup email")

    async def click_signup(self) -> None:
        await self.click(self.SIGNUP_BUTTON, msg="Click Signup")

    async def is_existing_email_error_visible(self) -> bool:
        return await self.is_visible(self.EXISTING_EMAIL_ERROR)

    # ---- Login ----
    async def is_login_to_account_visible(self) -> bool:
        return await self.is_visible(self.LOGIN_TO_ACCOUNT_TITLE)

    async def fill_login(self, email: str, password: str) -> None:
        await self.fill(self.LOGIN_EMAIL_INPUT, email, msg="Enter login email")
        await self.fill(self.LOGIN_PASSWORD_INPUT, password, msg="Enter login password")

    async def click_login(self) -> None:
        await self.click(self.LOGIN_BUTTON, msg="Click Login")

    async def is_login_error_visible(self) -> bool:
        return await self.is_visible(self.LOGIN_ERROR)
