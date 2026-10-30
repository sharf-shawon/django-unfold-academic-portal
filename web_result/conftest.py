from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from web_result.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from web_result.users.models import User


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()
