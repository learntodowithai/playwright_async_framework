"""Test Case 6: Contact Us Form."""
import pytest


@pytest.mark.ui
@pytest.mark.smoke
class TestContactUs:
    async def test_contact_us_form(self, ui, contact_details, upload_file_path):
        # 4: Open Contact Us page
        await ui.home.open()
        await ui.home.click_contact_us()

        # 5: Verify 'GET IN TOUCH'
        assert await ui.contact.is_get_in_touch_visible(), "'GET IN TOUCH' is not visible"

        # 6-7: Fill the form and upload a file
        await ui.contact.fill_contact_form(contact_details)
        await ui.contact.upload_file(upload_file_path)

        # 8-9: Submit and accept the pop-up
        await ui.contact.submit(contact_details, upload_file_path)

        # 10: Verify success message
        assert await ui.contact.is_success_visible(), "Contact form success message is not visible"

        # 11: Navigate Home and verify we landed on the home page
        await ui.contact.click_home()
        assert await ui.home.is_home_page_visible(), "Did not land back on the home page"
