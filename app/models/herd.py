"""Herd domain model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Herd(BaseModel):
    """Domain model representing a herd."""
    id: int = Field(..., description="Unique identifier for the herd")
    name: str = Field(..., description="Name of the herd")
    location: str = Field(..., description="Location of the herd")
    created_at: Optional[datetime] = Field(None, description="Timestamp of when the herd was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of when the herd was last updated")

    class Config:
        from_attributes = True # Allows creating model from ORM objects or dicts with attributes
        # For Pydantic v1, use: orm_mode = True