"""API endpoints related to the products list."""
from pages.API.base_api import BaseAPI


class ProductsAPI(BaseAPI):
    PRODUCTS_PATH = "/api/productsList"

    async def get_all_products(self):
        """API 1: GET all products list."""
        response = await self.get(self.PRODUCTS_PATH)
        return await self.parse(response)

    async def post_all_products(self):
        """API 2: POST to all products list (expected to be unsupported)."""
        response = await self.post(self.PRODUCTS_PATH)
        return await self.parse(response)
