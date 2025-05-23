"""Common dependencies for API endpoints."""

import logging
from sqlite3 import Connection
from typing import Generator

from ..core.database import get_db
from ..services import HerdService

logger = logging.getLogger(__name__)


def get_database() -> Generator[Connection, None, None]:
    """Database dependency."""
    with get_db() as db:
        yield db


def get_herd_service() -> HerdService:
    """Herd service dependency."""
    return HerdService()


# Common dependency aliases
Database = get_database
HerdServiceDep = get_herd_service