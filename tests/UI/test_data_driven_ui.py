"""Data-driven UI tests: contact form from JSON, product search from Excel."""
import os

import pytest

from utils.data_providers import ExcelDataProvider, JsonDataProvider, rows_as_parametrize

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "data")
CONTACT_JSON = os.path.abspath(os.path.join(DATA_DIR, "contact.json"))
PRODUCTS_XLSX = os.path.abspath(os.path.join(DATA_DIR, "products.xlsx"))

_contacts, _contact_ids = rows_as_parametrize(
    JsonDataProvider.read_rows(CONTACT_JSON), id_key="email"
)
_products, _product_ids = rows_as_parametrize(
    ExcelDataProvider.read_rows(PRODUCTS_XLSX), id_key="keyword"
)


@pytest.mark.ui
@pytest.mark.parametrize("contact", _contacts, ids=_contact_ids)
class TestContactFromJson:
    async def test_contact_form_from_json(self, ui, contact, upload_file_path):
        """TC6 style: submit the contact form with data read from a JSON file."""
        await ui.home.open()
        await ui.home.click_contact_us()
        assert await ui.contact.is_get_in_touch_visible(), "'GET IN TOUCH' is not visible"

        await ui.contact.fill_contact_form(contact)
        await ui.contact.upload_file(upload_file_path)
        await ui.contact.submit(contact, upload_file_path)

        assert await ui.contact.is_success_visible(), "Contact form success message is not visible"
        await ui.contact.click_home()
        assert await ui.home.is_home_page_visible(), "Did not land back on the home page"


@pytest.mark.ui
@pytest.mark.parametrize("product", _products, ids=_product_ids)
class TestProductsFromExcel:
    async def test_search_products_from_excel(self, ui, product):
        """TC9 style: search for products using keywords read from an Excel file."""
        await ui.home.open()
        await ui.products.open()
        await ui.products.search_product(product["keyword"])

        assert await ui.products.is_searched_products_visible(), "'SEARCHED PRODUCTS' title is not visible"
        results = ui.products.page.locator(ui.products.PRODUCT_CARD)
        assert await results.count() >= int(product["min_count"]), \
            f"Expected at least {product['min_count']} product(s) for '{product['keyword']}'"
