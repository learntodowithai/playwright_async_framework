"""Page object for the order-success screen (invoice download etc.)."""
from playwright.async_api import expect

from pages.base_page import BasePage


class OrderSuccessPage(BasePage):
    ORDER_PLACED_TITLE = "text=Congratulations! Your order has been confirmed!"
    DOWNLOAD_INVOICE_BUTTON = 'a[href*="/download_invoice/"]'
    CONTINUE_BUTTON = 'a[data-qa="continue-button"]'

    async def is_order_placed_visible(self) -> bool:
        return await self.wait_for_element_visible(self.ORDER_PLACED_TITLE, timeout=15000)

    async def click_download_invoice(self, save_path: str) -> None:
        async with self.page.expect_download() as download_info:
            await self.click(self.DOWNLOAD_INVOICE_BUTTON, msg="Download invoice")
        download = await download_info.value
        await download.save_as(save_path)

    async def click_continue(self) -> None:
        await self.click(self.CONTINUE_BUTTON, msg="Continue after order")
