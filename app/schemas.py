from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional


class HerdBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the herd")
    location: str = Field(..., min_length=1, max_length=200, description="Location of the herd")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Location cannot be empty or whitespace only')
        return v.strip()


class HerdCreate(HerdBase):
    pass


class HerdUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip() if v else v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('Location cannot be empty or whitespace only')
        return v.strip() if v else v


class Herd(HerdBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="Unique identifier for the herd")
