"""Herd domain model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Herd:
    """Domain model representing a herd."""
    id: int
    name: str
    location: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None