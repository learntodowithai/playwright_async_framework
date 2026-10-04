"""Shared fixtures for the API test suite.

Core fixtures (``api``, ``new_user``, ``created_user`` and the auth-state
helpers) now live in the shared :mod:`auth.fixtures` plugin, registered via
``pytest_plugins`` in the root ``conftest.py``. This suite has nothing
API-suite-specific to add, so only the docstring remains.
"""
