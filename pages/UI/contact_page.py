"""Page object for the Contact Us form page."""
from playwright.async_api import expect

from pages.base_page import BasePage


class ContactPage(BasePage):
    GET_IN_TOUCH_TITLE = "text=GET IN TOUCH"
    NAME_INPUT = 'input[data-qa="name"]'
    EMAIL_INPUT = 'input[data-qa="email"]'
    SUBJECT_INPUT = 'input[data-qa="subject"]'
    MESSAGE_TEXTAREA = 'textarea[data-qa="message"]'
    UPLOAD_FILE_INPUT = 'input[name="upload_file"]'
    SUBMIT_BUTTON = 'input[data-qa="submit-button"]'
    SUCCESS_MESSAGE = "text=Success! Your details have been submitted successfully."
    HOME_BUTTON = "#form-section a[href='/']"

    async def open(self) -> None:
        await self.goto("/contact_us")

    async def is_get_in_touch_visible(self) -> bool:
        return await self.is_visible(self.GET_IN_TOUCH_TITLE)

    async def fill_contact_form(self, details: dict) -> None:
        await self.fill(self.NAME_INPUT, details["name"], msg="Enter contact name")
        await self.fill(self.EMAIL_INPUT, details["email"], msg="Enter contact email")
        await self.fill(self.SUBJECT_INPUT, details["subject"], msg="Enter subject")
        await self.fill(self.MESSAGE_TEXTAREA, details["message"], msg="Enter message")

    async def upload_file(self, file_path: str) -> None:
        await self.page.locator(self.UPLOAD_FILE_INPUT).set_input_files(file_path)

    async def submit(self, details: dict | None = None, file_path: str | None = None) -> None:
        """Submit the form, accepting the confirm dialog.

        The site binds its submit handler via jQuery; if it is not attached yet
        (race right after navigation) the form would POST directly with no
        dialog. Detect that and retry once on a freshly loaded page.
        """
        import asyncio

        dialog_fired = asyncio.Event()

        async def _accept(dialog):
            dialog_fired.set()
            await dialog.accept()

        self.page.on("dialog", _accept)

        for attempt in range(2):
            await self.click(self.SUBMIT_BUTTON, msg="Submit contact form")
            try:
                await asyncio.wait_for(dialog_fired.wait(), timeout=10)
                return
            except asyncio.TimeoutError:
                if attempt == 1:
                    raise
                await self.page.wait_for_load_state("load")
                await self.open()
                if details:
                    await self.fill_contact_form(details)
                if file_path:
                    await self.upload_file(file_path)

    async def is_success_visible(self) -> bool:
        return await self.wait_for_element_visible(self.SUCCESS_MESSAGE, timeout=10000)

    async def click_home(self) -> None:
        await self.click(self.HOME_BUTTON, msg="Go Home from contact page")
