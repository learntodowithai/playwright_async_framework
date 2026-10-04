"""API endpoints related to product search."""
from pages.API.base_api import BaseAPI


class SearchAPI(BaseAPI):
    SEARCH_PATH = "/api/searchProduct"

    async def search_product(self, search_term: str):
        """API 5: POST to search product with a valid search_product parameter."""
        response = await self.post(self.SEARCH_PATH, form={"search_product": search_term})
        return await self.parse(response)

    async def search_product_without_param(self):
        """API 6: POST to search product without the search_product parameter."""
        response = await self.post(self.SEARCH_PATH)
        return await self.parse(response)
