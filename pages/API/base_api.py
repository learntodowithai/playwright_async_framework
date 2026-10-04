"""Base client for the automationexercise.com REST API."""
from typing import Any, Dict, Optional

from playwright.async_api import APIRequestContext, APIResponse


class BaseAPI:
    """Thin wrapper over Playwright's APIRequestContext."""

    def __init__(self, request_context: APIRequestContext):
        self.request = request_context

    # ---- HTTP verbs ------------------------------------------------------ #
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return await self.request.get(path, params=params, **kwargs)

    async def post(self, path: str, form: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return await self.request.post(path, form=form, **kwargs)

    async def put(self, path: str, form: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return await self.request.put(path, form=form, **kwargs)

    async def delete(self, path: str, form: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return await self.request.delete(path, form=form, **kwargs)

    # ---- Response helpers ------------------------------------------------ #
    @staticmethod
    async def parse(response: APIResponse) -> Dict[str, Any]:
        """Parse the JSON body of an API response."""
        try:
            return await response.json()
        except Exception:
            import json as _json
            return _json.loads(await response.text())

    @staticmethod
    def response_code(data: Dict[str, Any]) -> int:
        """The automationexercise API mirrors the logical status inside the body."""
        try:
            return int(data.get("responseCode", -1))
        except (TypeError, ValueError):
            return -1

    @staticmethod
    def message(data: Dict[str, Any]) -> str:
        return str(data.get("message", ""))

    def assert_response(self, data: Dict[str, Any], expected_code: int, expected_message: Optional[str] = None) -> None:
        """Validate the logical response code and optional message."""
        actual_code = self.response_code(data)
        assert actual_code == expected_code, (
            f"Expected responseCode {expected_code} but got {actual_code}. Body: {data}"
        )
        if expected_message is not None:
            assert self.message(data) == expected_message, (
                f"Expected message '{expected_message}' but got '{self.message(data)}'."
            )
