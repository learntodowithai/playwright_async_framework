"""Authentication state model and state-machine transitions.

This module decouples *what* authentication state a browser/session is in from
*how* it is achieved. Test code can request an auth state through the fixtures
in :mod:`auth.fixtures` or drive transitions directly through
:class:`AuthTransitions`.

States
------
``AuthState.GUEST``      - browsing anonymously (not logged in).
``AuthState.LOGGED_IN``  - an authenticated session for a known user.

Transitions are implemented as static methods that accept the page-object
collection (``ui``) and/or the API-client collection (``api``) - the same
``SimpleNamespace`` objects produced by the shared fixtures - and return an
:class:`AuthSession` describing the resulting state. Cleanup is intentionally
left to the caller (typically a pytest fixture teardown) so transitions stay
composable.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class AuthState(Enum):
    """Discrete authentication states a session can occupy."""

    GUEST = "guest"
    LOGGED_IN = "logged_in"


@dataclass
class AuthSession:
    """Snapshot of a session's authentication state.

    ``user`` is the test-user dict (name/email/password plus profile fields)
    the session belongs to, or ``None`` for a guest session.
    """

    state: AuthState
    user: Optional[dict] = None

    @property
    def is_authenticated(self) -> bool:
        return self.state == AuthState.LOGGED_IN

    @property
    def display_name(self) -> str:
        return self.user["name"] if self.user else "guest"

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"{self.state.value}({self.display_name})"


class AuthTransitions:
    """State-machine transitions between :class:`AuthState` values.

    ``ui`` and ``api`` are the ``SimpleNamespace`` collections built by the
    ``ui`` and ``api`` fixtures; they are typed as ``Any`` to keep this module
    decoupled from the concrete page/API classes.
    """

    # ------------------------------------------------------------------ #
    # Guest
    # ------------------------------------------------------------------ #
    @staticmethod
    def guest() -> AuthSession:
        """The default, unauthenticated state."""
        return AuthSession(AuthState.GUEST)

    # ------------------------------------------------------------------ #
    # Account lifecycle (REST API)
    # ------------------------------------------------------------------ #
    @staticmethod
    async def create_account(user: dict, api: Any) -> None:
        """Create a user account through the REST API (no UI session)."""
        data = await api.account.create_account(user)
        api.account.assert_response(data, 201, "User created!")

    @staticmethod
    async def delete_account(user: dict, api: Any) -> None:
        """Delete a user account through the REST API (best-effort)."""
        try:
            await api.account.delete_account(user["email"], user["password"])
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # UI flows
    # ------------------------------------------------------------------ #
    @staticmethod
    async def register_and_login(user: dict, ui: Any) -> AuthSession:
        """Full sign-up journey through the UI, landing on the home page."""
        await ui.auth.open()
        await ui.auth.fill_signup(user["name"], user["email"])
        await ui.auth.click_signup()
        await ui.signup.fill_account_details(user)
        await ui.signup.create_account()
        assert await ui.account.is_account_created_visible(), "ACCOUNT CREATED! not shown"
        await ui.account.click_continue()
        assert await ui.home.is_logged_in_as(user["name"]), "User is not logged in"
        return AuthSession(AuthState.LOGGED_IN, user=user)

    @staticmethod
    async def login(user: dict, ui: Any) -> AuthSession:
        """Perform an existing-user login through the UI."""
        await ui.auth.open()
        await ui.auth.fill_login(user["email"], user["password"])
        await ui.auth.click_login()
        assert await ui.home.is_logged_in_as(user["name"]), "User is not logged in"
        return AuthSession(AuthState.LOGGED_IN, user=user)

    @staticmethod
    async def logout(ui: Any) -> AuthSession:
        """Log the current user out via the header link."""
        await ui.home.open()
        await ui.home.click_logout()
        assert await ui.auth.is_login_to_account_visible(), "User was not navigated to the login page"
        return AuthSession(AuthState.GUEST)

    @staticmethod
    async def delete_account_via_ui(user: dict, ui: Any) -> None:
        """Delete the logged-in user's account through the UI (best-effort)."""
        try:
            await ui.home.click_delete_account()
            assert await ui.account.is_account_deleted_visible(), "ACCOUNT DELETED! not shown"
            await ui.account.click_continue()
        except Exception:
            pass
