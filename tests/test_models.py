"""Test data models."""

import pytest
from datetime import datetime
from app.models.user import AuthenticatedUserModel
from app.models.herd import HerdModel
from app.schemas import User, HerdCreate, HerdResponse


def test_authenticated_user_model():
    """Test AuthenticatedUserModel."""
    user = AuthenticatedUserModel(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        disabled=False
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.disabled is False


def test_authenticated_user_model_from_db_user():
    """Test creating AuthenticatedUserModel from database user."""
    db_user = {
        "username": "dbuser",
        "email": "db@example.com",
        "full_name": "DB User",
        "disabled": False
    }
    
    user = AuthenticatedUserModel.from_db_user(db_user)
    assert user.username == "dbuser"
    assert user.email == "db@example.com"
    assert user.full_name == "DB User"
    assert user.disabled is False


def test_herd_model():
    """Test HerdModel."""
    herd = HerdModel(
        id=1,
        name="Test Farm",
        location="Test Location",
        description="Test Description",
        size=100,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert herd.id == 1
    assert herd.name == "Test Farm"
    assert herd.location == "Test Location"
    assert herd.size == 100


def test_user_schema():
    """Test User schema."""
    user = User(
        username="schemauser",
        email="schema@example.com",
        full_name="Schema User"
    )
    
    assert user.username == "schemauser"
    assert user.email == "schema@example.com"
    assert user.full_name == "Schema User"


def test_herd_create_schema():
    """Test HerdCreate schema."""
    herd_data = HerdCreate(
        name="New Farm",
        location="New Location",
        description="New Description",
        size=50
    )
    
    assert herd_data.name == "New Farm"
    assert herd_data.location == "New Location"
    assert herd_data.size == 50


def test_herd_response_schema():
    """Test HerdResponse schema."""
    herd_response = HerdResponse(
        id=1,
        name="Response Farm",
        location="Response Location",
        description="Response Description",
        size=75,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert herd_response.id == 1
    assert herd_response.name == "Response Farm"
    assert herd_response.size == 75