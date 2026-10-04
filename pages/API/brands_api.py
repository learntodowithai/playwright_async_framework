"""API endpoints related to the brands list."""
from pages.API.base_api import BaseAPI


class BrandsAPI(BaseAPI):
    BRANDS_PATH = "/api/brandsList"

    async def get_all_brands(self):
        """API 3: GET all brands list."""
        response = await self.get(self.BRANDS_PATH)
        return await self.parse(response)

    async def put_all_brands(self):
        """API 4: PUT to all brands list (expected to be unsupported)."""
        response = await self.put(self.BRANDS_PATH)
        return await self.parse(response)
