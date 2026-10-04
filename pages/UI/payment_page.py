"""Page object for the payment details page."""
from playwright.async_api import expect

from pages.base_page import BasePage


class PaymentPage(BasePage):
    NAME_ON_CARD_INPUT = 'input[data-qa="name-on-card"]'
    CARD_NUMBER_INPUT = 'input[data-qa="card-number"]'
    CVC_INPUT = 'input[data-qa="cvc"]'
    EXPIRY_MONTH_INPUT = 'input[data-qa="expiry-month"]'
    EXPIRY_YEAR_INPUT = 'input[data-qa="expiry-year"]'
    PAY_BUTTON = 'button[data-qa="pay-button"]'

    async def is_payment_page_visible(self) -> bool:
        return await self.wait_for_element_visible(self.PAY_BUTTON, timeout=20000)

    async def fill_payment_details(self, payment: dict) -> None:
        await self.fill(self.NAME_ON_CARD_INPUT, payment["name_on_card"], msg="Enter name on card")
        await self.fill(self.CARD_NUMBER_INPUT, payment["card_number"], msg="Enter card number")
        await self.fill(self.CVC_INPUT, payment["cvc"], msg="Enter CVC")
        await self.fill(self.EXPIRY_MONTH_INPUT, payment["expiry_month"], msg="Enter expiry month")
        await self.fill(self.EXPIRY_YEAR_INPUT, payment["expiry_year"], msg="Enter expiry year")

    async def click_pay_and_confirm(self) -> None:
        await self.click(self.PAY_BUTTON, msg="Pay and confirm order")
