"""Authentication state model and reusable auth fixtures.

Public API:
    ``AuthState``         - enum of discrete authentication states.
    ``AuthSession``       - dataclass snapshot of a session's auth state.
    ``AuthTransitions``   - state-machine transitions between auth states.

The matching pytest fixtures live in :mod:`auth.fixtures` and are registered
centrally via ``pytest_plugins`` in the root ``conftest.py`` so that every
suite (UI, API, hybrid) shares a single source of truth.
"""
from auth.states import AuthState, AuthSession, AuthTransitions

__all__ = ["AuthState", "AuthSession", "AuthTransitions"]
