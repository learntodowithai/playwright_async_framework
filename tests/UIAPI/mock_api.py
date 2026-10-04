"""Helpers to mock and capture the API calls triggered by UI actions.

Every UI test in this suite drives real UI actions (clicks, form submits,
navigations). Some of those actions make an AJAX call to the application's
API - for example cart.js calls ``GET /add_to_cart/<id>`` and
``GET /delete_cart/<id>``. ``MockAPI`` installs Playwright route handlers that
either:

* **mock** the call (``route.fulfill`` with a controlled body) so the UI
  behaviour is deterministic, or
* **capture** the call (``route.continue_``) so the request the UI really sent
  reaches the backend and its method / URL / payload can be asserted.

Requests are recorded and later verified with the ``expect_requested`` helpers,
which is what turns this into a UI + API integration test.
"""
import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from playwright.async_api import Page, Request, Route

from .mock_data import FAILURE_RESPONSE, SUCCESS_RESPONSE

RequestHandler = Any  # async (Route, Request) -> None


class CapturedRequest:
    """Snapshot of a browser network request fired by a UI action."""

    def __init__(self, request: Request):
        self.method = request.method.upper()
        self.url = request.url
        self.headers = request.headers
        self.post_data = request.post_data
        self.query = self._parse_query(request.url)

    @staticmethod
    def _parse_query(url: str) -> Dict[str, List[str]]:
        return parse_qs(urlsplit(url).query)

    @property
    def path(self) -> str:
        return urlsplit(self.url).path

    def __repr__(self) -> str:
        return f"<CapturedRequest {self.method} {self.url}>"


class MockAPI:
    """Registers mocked / captured routes on a page and records the traffic."""

    def __init__(self, page: Page):
        self.page = page
        self._captured: List[CapturedRequest] = []
        self._routes: List[Tuple[str, RequestHandler]] = []

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    async def _add_route(
        self,
        pattern: str,
        *,
        method: Optional[str] = None,
        record: bool = True,
        handler: Optional[RequestHandler] = None,
    ) -> None:
        async def route_handler(route: Route) -> None:
            request = route.request
            if method and request.method.upper() != method.upper():
                await route.continue_()
                return
            if record:
                self._captured.append(CapturedRequest(request))
            if handler is not None:
                await handler(route, request)
            else:
                await route.continue_()

        await self.page.route(pattern, route_handler)
        self._routes.append((pattern, route_handler))

    async def capture(self, pattern: str, method: Optional[str] = None) -> None:
        """Record matching requests and forward them to the real server."""
        await self._add_route(pattern, method=method, record=True)

    async def mock_json(
        self,
        pattern: str,
        payload: Dict[str, Any],
        *,
        status: int = 200,
        method: Optional[str] = None,
        record: bool = True,
    ) -> None:
        """Fulfil matching requests with a controlled JSON body."""

        async def handler(route: Route, _request: Request) -> None:
            await route.fulfill(
                status=status,
                content_type="application/json",
                body=json.dumps(payload),
            )

        await self._add_route(pattern, method=method, record=record, handler=handler)

    async def mock_html(
        self,
        pattern: str,
        body: str,
        *,
        status: int = 200,
        method: Optional[str] = None,
        record: bool = True,
    ) -> None:
        """Fulfil matching requests with a controlled HTML body."""

        async def handler(route: Route, _request: Request) -> None:
            await route.fulfill(
                status=status,
                content_type="text/html; charset=utf-8",
                body=body,
            )

        await self._add_route(pattern, method=method, record=record, handler=handler)

    # Convenience wrappers for the cart endpoints the UI triggers.
    async def mock_cart_add(self, *, status: int = 200) -> None:
        await self.mock_json("**/add_to_cart/**", SUCCESS_RESPONSE, status=status, method="GET")

    async def mock_cart_add_failure(self, *, status: int = 500) -> None:
        await self.mock_json("**/add_to_cart/**", FAILURE_RESPONSE, status=status, method="GET")

    async def mock_cart_delete(self, *, status: int = 200) -> None:
        await self.mock_json("**/delete_cart/**", SUCCESS_RESPONSE, status=status, method="GET")

    async def capture_cart_add(self) -> None:
        await self.capture("**/add_to_cart/**", method="GET")

    # ------------------------------------------------------------------ #
    # Inspection / assertions
    # ------------------------------------------------------------------ #
    def requests(
        self,
        url_contains: Optional[str] = None,
        method: Optional[str] = None,
    ) -> List[CapturedRequest]:
        matches = self._captured
        if url_contains:
            matches = [r for r in matches if url_contains in r.url]
        if method:
            matches = [r for r in matches if r.method.upper() == method.upper()]
        return matches

    def last_request(
        self,
        url_contains: Optional[str] = None,
        method: Optional[str] = None,
    ) -> Optional[CapturedRequest]:
        matches = self.requests(url_contains, method)
        return matches[-1] if matches else None

    async def wait_for_request(
        self,
        url_contains: str,
        method: Optional[str] = None,
        timeout: int = 10000,
    ) -> CapturedRequest:
        """Wait until the UI has fired a matching request (avoids race conditions)."""
        import asyncio
        from datetime import datetime, timedelta

        deadline = datetime.now() + timedelta(milliseconds=timeout)
        while datetime.now() < deadline:
            match = self.last_request(url_contains, method)
            if match is not None:
                return match
            await asyncio.sleep(0.1)
        raise AssertionError(
            f"UI never fired a request containing '{url_contains}' "
            f"(method={method or 'any'}). Captured: {[r.url for r in self._captured]}"
        )

    def expect_requested(
        self,
        url_contains: str,
        method: Optional[str] = None,
    ) -> CapturedRequest:
        """Return the latest captured request, failing the test if none."""
        match = self.last_request(url_contains, method)
        assert match is not None, (
            f"No captured request containing '{url_contains}' "
            f"(method={method or 'any'}). Captured: {[r.url for r in self._captured]}"
        )
        return match

    def expect_post_data(self, url_contains: str, expected: Dict[str, str]) -> None:
        """Assert the URL-encoded POST body of a captured request has values."""
        match = self.expect_requested(url_contains, method="POST")
        actual = parse_qs(match.post_data or "")
        for key, value in expected.items():
            assert key in actual, (
                f"POST body missing field '{key}'. Actual: {actual}"
            )
            assert value in actual[key], (
                f"POST field '{key}' expected to contain '{value}'. Actual: {actual[key]}"
            )

    async def unroute_all(self) -> None:
        """Remove every route handler installed by this helper."""
        for pattern, _handler in self._routes:
            try:
                await self.page.unroute(pattern)
            except Exception:
                pass
        self._routes.clear()