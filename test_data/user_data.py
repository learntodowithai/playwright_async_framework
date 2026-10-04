"""Static test data values used by the UI and API test suites."""

# Header navigation labels
NAV = {
    "signup_login": "Signup / Login",
    "products": "Products",
    "cart": "Cart",
    "test_cases": "Test Cases",
    "contact_us": "Contact us",
}

# Expected status/message assertions for the REST API
API_EXPECTED = {
    "products_get": {"code": 200},
    "products_post_405": {"code": 405, "message": "This request method is not supported."},
    "brands_get": {"code": 200},
    "brands_put_405": {"code": 405, "message": "This request method is not supported."},
    "search_400": {"code": 400, "message": "Bad request, search_product parameter is missing in POST request."},
    "login_missing_param_400": {"code": 400, "message": "Bad request, email or password parameter is missing in POST request."},
    "login_valid_200": {"code": 200, "message": "User exists!"},
    "login_invalid_404": {"code": 404, "message": "User not found!"},
    "login_delete_405": {"code": 405, "message": "This request method is not supported."},
    "create_account_201": {"code": 201, "message": "User created!"},
    "delete_account_200": {"code": 200, "message": "Account deleted!"},
    "update_account_200": {"code": 200, "message": "User updated!"},
}


