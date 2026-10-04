"""Page object for the account information (sign-up details) form."""
from playwright.async_api import expect

from pages.base_page import BasePage


class SignupPage(BasePage):
    ENTER_ACCOUNT_TITLE = "text=ENTER ACCOUNT INFORMATION"

    TITLE_MR = "#id_gender1"
    TITLE_MRS = "#id_gender2"
    PASSWORD_INPUT = "#password"
    DAYS_SELECT = "#days"
    MONTHS_SELECT = "#months"
    YEARS_SELECT = "#years"
    NEWSLETTER_CHECKBOX = "#newsletter"
    OPTIN_CHECKBOX = "#optin"

    FIRST_NAME_INPUT = "#first_name"
    LAST_NAME_INPUT = "#last_name"
    COMPANY_INPUT = "#company"
    ADDRESS1_INPUT = "#address1"
    ADDRESS2_INPUT = "#address2"
    COUNTRY_SELECT = "#country"
    STATE_INPUT = "#state"
    CITY_INPUT = "#city"
    ZIPCODE_INPUT = "#zipcode"
    MOBILE_NUMBER_INPUT = "#mobile_number"

    CREATE_ACCOUNT_BUTTON = 'button[data-qa="create-account"]'

    async def is_enter_account_info_visible(self) -> bool:
        return await self.is_visible(self.ENTER_ACCOUNT_TITLE)

    async def select_title(self, title: str) -> None:
        selector = self.TITLE_MR if title.lower() == "mr" else self.TITLE_MRS
        await self.click(selector, msg=f"Select title {title}")

    async def fill_account_details(self, user: dict) -> None:
        await self.select_title(user["title"])
        await self.fill(self.PASSWORD_INPUT, user["password"], msg="Enter password")
        await self.page.locator(self.DAYS_SELECT).select_option(user["birth_date"])
        await self.page.locator(self.MONTHS_SELECT).select_option(user["birth_month"])
        await self.page.locator(self.YEARS_SELECT).select_option(user["birth_year"])
        await self.click(self.NEWSLETTER_CHECKBOX, msg="Subscribe to newsletter")
        await self.click(self.OPTIN_CHECKBOX, msg="Receive special offers")
        await self.fill(self.FIRST_NAME_INPUT, user["first_name"], msg="Enter first name")
        await self.fill(self.LAST_NAME_INPUT, user["last_name"], msg="Enter last name")
        await self.fill(self.COMPANY_INPUT, user["company"], msg="Enter company")
        await self.fill(self.ADDRESS1_INPUT, user["address1"], msg="Enter address 1")
        await self.fill(self.ADDRESS2_INPUT, user["address2"], msg="Enter address 2")
        await self.page.locator(self.COUNTRY_SELECT).select_option(user["country"])
        await self.fill(self.STATE_INPUT, user["state"], msg="Enter state")
        await self.fill(self.CITY_INPUT, user["city"], msg="Enter city")
        await self.fill(self.ZIPCODE_INPUT, user["zipcode"], msg="Enter zipcode")
        await self.fill(self.MOBILE_NUMBER_INPUT, user["mobile_number"], msg="Enter mobile number")

    async def create_account(self) -> None:
        await self.click(self.CREATE_ACCOUNT_BUTTON, msg="Create account")
