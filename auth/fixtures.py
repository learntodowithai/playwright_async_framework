"""Shared, reusable fixtures for auth and page/API object wiring.

These fixtures are registered centrally via ``pytest_plugins`` in the root
``conftest.py`` so that every test suite (UI, API, hybrid) shares a single
source of truth for:

  * user factories (``new_user``)
  * page-object collections (``ui``)
  * API-client collections (``api``)
  * auth-state sessions (``guest_session``, ``logged_in_session``,
    ``auth_session``) and the transition state machine (``auth_state_factory``)

This removes the per-suite duplication that previously existed.
"""
from types import SimpleNamespace

import pytest

from pages.UI.account_page import AccountPage
from pages.UI.auth_page import AuthPage
from pages.UI.cart_page import CartPage
from pages.UI.checkout_page import CheckoutPage
from pages.UI.contact_page import ContactPage
from pages.UI.home_page import HomePage
from pages.UI.order_success_page import OrderSuccessPage
from pages.UI.payment_page import PaymentPage
from pages.UI.product_details_page import ProductDetailsPage
from pages.UI.products_page import ProductsPage
from pages.UI.signup_page import SignupPage
from pages.UI.test_cases_page import TestCasesPage
from pages.API.account_api import AccountAPI
from pages.API.brands_api import BrandsAPI
from pages.API.login_api import LoginAPI
from pages.API.products_api import ProductsAPI
from pages.API.search_api import SearchAPI
from utils.data_generator import new_user as generate_user

from auth.states import AuthSession, AuthState, AuthTransitions


# --------------------------------------------------------------------------- #
# User factory
# --------------------------------------------------------------------------- #
@pytest.fixture
def new_user() -> dict:
    """A fresh, unique user payload used for sign-up / login flows."""
    return generate_user()


# --------------------------------------------------------------------------- #
# Page-object & API-client collections
# --------------------------------------------------------------------------- #
@pytest.fixture
async def ui(page):
    """Collection of UI page objects bound to the current browser page."""
    return SimpleNamespace(
        home=HomePage(page),
        auth=AuthPage(page),
        signup=SignupPage(page),
        account=AccountPage(page),
        products=ProductsPage(page),
        product_details=ProductDetailsPage(page),
        cart=CartPage(page),
        checkout=CheckoutPage(page),
        payment=PaymentPage(page),
        order_success=OrderSuccessPage(page),
        contact=ContactPage(page),
        test_cases=TestCasesPage(page),
    )


@pytest.fixture
def api(api_request_context):
    """Collection of API clients bound to the shared API request context."""
    return SimpleNamespace(
        products=ProductsAPI(api_request_context),
        brands=BrandsAPI(api_request_context),
        search=SearchAPI(api_request_context),
        login=LoginAPI(api_request_context),
        account=AccountAPI(api_request_context),
    )


# --------------------------------------------------------------------------- #
# Shared auth helpers
# --------------------------------------------------------------------------- #
async def _cleanup_user(api, user: dict) -> None:
    """Best-effort cleanup of a user account created for a test."""
    await AuthTransitions.delete_account(user, api)


# --------------------------------------------------------------------------- #
# Seeding / preparation fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
async def existing_user(api, new_user):
    """A user account created through the REST API (not logged in on the UI).

    Useful for tests that perform their own login journey, e.g. Test Case 2
    (login with correct credentials) and Test Case 5 (register with existing
    email).
    """
    await AuthTransitions.create_account(new_user, api)
    yield new_user
    await _cleanup_user(api, new_user)


@pytest.fixture
async def registered_user(ui, new_user, api):
    """A user registered through the UI and currently logged in on the home page."""
    await AuthTransitions.register_and_login(new_user, ui)
    yield new_user
    await _cleanup_user(api, new_user)


@pytest.fixture
async def created_user(api, new_user):
    """An account created through the API; deleted automatically afterwards."""
    await AuthTransitions.create_account(new_user, api)
    yield new_user
    await _cleanup_user(api, new_user)


@pytest.fixture
async def api_created_user(created_user):
    """Alias of ``created_user`` for the hybrid suite naming convention."""
    return created_user


# --------------------------------------------------------------------------- #
# Auth-state sessions (the enhanced, reusable surface)
# --------------------------------------------------------------------------- #
@pytest.fixture
async def guest_session(ui):
    """An anonymous browsing session (not logged in), landed on the home page."""
    await ui.home.open()
    yield AuthSession(AuthState.GUEST)


@pytest.fixture
async def logged_in_session(ui, new_user, api):
    """A freshly registered + logged-in user session, cleaned up afterwards.

    Returns an :class:`AuthSession` (state=LOGGED_IN) the test can assert
    against, rather than a bare user dict - useful when the test wants to
    branch logic on the auth state rather than just use the credentials.
    """
    await AuthTransitions.register_and_login(new_user, ui)
    yield AuthSession(AuthState.LOGGED_IN, user=new_user)
    await _cleanup_user(api, new_user)


@pytest.fixture
async def auth_session(request, ui, new_user, api):
    """Parametrized auth session for running a test across multiple states.

    Default (no parametrization)::

        async def test_something(auth_session, ui): ...   # -> logged_in

    Drive both states with indirect parametrization::

        @pytest.mark.parametrize("auth_session", ["guest", "logged_in"], indirect=True)
        async def test_something(auth_session, ui): ...

    Acceptable values: ``"guest"`` / ``AuthState.GUEST`` and
    ``"logged_in"`` / ``AuthState.LOGGED_IN``.
    """
    param = getattr(request, "param", AuthState.LOGGED_IN.value)
    state = param.value if isinstance(param, AuthState) else param
    if state in (AuthState.GUEST.value, "guest"):
        await ui.home.open()
        session = AuthSession(AuthState.GUEST)
    else:
        await AuthTransitions.register_and_login(new_user, ui)
        session = AuthSession(AuthState.LOGGED_IN, user=new_user)
    yield session
    if session.is_authenticated:
        await _cleanup_user(api, new_user)


@pytest.fixture
def auth_state_factory():
    """Factory giving direct access to :class:`AuthTransitions` methods.

    Use this when a test needs to compose transitions on the fly::

        async def test_logout_then_login(auth_state_factory, ui, existing_user):
            await auth_state_factory.login(existing_user, ui)
            await auth_state_factory.logout(ui)
    """
    return AuthTransitions
