"""Page object for account confirmation screens (created / deleted)."""
from playwright.async_api import expect

from pages.base_page import BasePage


class AccountPage(BasePage):
    ACCOUNT_CREATED_TITLE = "text=ACCOUNT CREATED!"
    ACCOUNT_DELETED_TITLE = "text=ACCOUNT DELETED!"
    CONTINUE_BUTTON = 'a[data-qa="continue-button"]'

    async def is_account_created_visible(self) -> bool:
        return await self.is_visible(self.ACCOUNT_CREATED_TITLE)

    async def is_account_deleted_visible(self) -> bool:
        return await self.is_visible(self.ACCOUNT_DELETED_TITLE)

    async def click_continue(self) -> None:
        await self.click(self.CONTINUE_BUTTON, msg="Continue after account action")
