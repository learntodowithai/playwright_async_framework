"""Mocked API payloads returned to the UI when its AJAX calls are intercepted.

The automationexercise.com front-end triggers these endpoints while you use
the site. When a test mocks one of them, the browser receives the payload
below instead of the real backend response - so the UI behaviour is fully
deterministic and independent of the server state.
"""

#: Generic success body returned to cart AJAX calls (add / delete).
#: cart.js only inspects the HTTP status, not the body, so this is enough.
SUCCESS_RESPONSE = {"success": True, "message": "Mocked by UI+API test"}

#: Response body used when a test wants the UI to treat the call as failed.
FAILURE_RESPONSE = {"success": False, "message": "Mocked failure"}

#: A controlled product that the mock product APIs return. Used when a test
#: deliberately feeds the UI a synthetic catalog to prove the page renders
#: whatever the (mocked) API provides.
MOCKED_PRODUCT = {
    "id": 999,
    "name": "Mocked Test Product",
    "price": "Rs. 123",
    "brand": "Polo",
    "category": {
        "usertype": {"usertype": "Women"},
        "category": "Tops",
    },
}