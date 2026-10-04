"""Shared fixtures for the UI + API integration suite.

Core fixtures (``new_user``, ``ui``, ``api`` and the auth-state helpers) now
live in the shared :mod:`auth.fixtures` plugin, registered via
``pytest_plugins`` in the root ``conftest.py``. Only the hybrid-suite-specific
``mock_api`` fixture remains here.
"""
import pytest

from .mock_api import MockAPI


@pytest.fixture
async def mock_api(page):
    """Mock / capture helper bound to the current browser page."""
    mock = MockAPI(page)
    yield mock
    await mock.unroute_all()
