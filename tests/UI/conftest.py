"""Shared fixtures for the UI test suite.

Core fixtures (``new_user``, ``ui``, ``api``, auth-state sessions and the
seeding helpers ``existing_user`` / ``registered_user``) now live in the shared
:mod:`auth.fixtures` plugin, registered via ``pytest_plugins`` in the root
``conftest.py``. Only UI-suite-specific fixtures remain here.
"""
from pathlib import Path

import pytest

from config.settings import settings
from utils.data_generator import contact_message

ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def contact_details() -> dict:
    return contact_message()


@pytest.fixture
def upload_file_path() -> str:
    return str(ROOT / settings.CONTACT_FILE)
