"""Test core security functions."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user,
    get_user
)
from app.exceptions import AuthenticationError


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test with custom expiration
    token_with_expiry = create_access_token(
        data, expires_delta=timedelta(minutes=30)
    )
    assert isinstance(token_with_expiry, str)
    assert token != token_with_expiry  # Should be different due to exp claim


def test_verify_token_success():
    """Test token verification success."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_verify_token_invalid():
    """Test token verification with invalid token."""
    with pytest.raises(AuthenticationError):
        verify_token("invalid.token.here")


def test_verify_token_expired():
    """Test token verification with expired token."""
    data = {"sub": "testuser"}
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(AuthenticationError):
        verify_token(token)


@patch('app.core.security.user_service.get_user')
def test_get_user(mock_get_user):
    """Test get_user function."""
    mock_user = {"username": "testuser", "email": "test@example.com"}
    mock_get_user.return_value = mock_user
    
    result = get_user("testuser")
    assert result == mock_user
    mock_get_user.assert_called_once_with("testuser")


@patch('app.core.security.get_user')
@patch('app.core.security.verify_password')
def test_authenticate_user_success(mock_verify, mock_get_user):
    """Test successful user authentication."""
    mock_user = {
        "username": "testuser",
        "email": "test@example.com", 
        "hashed_password": "hashed_pass",
        "disabled": False
    }
    mock_get_user.return_value = mock_user
    mock_verify.return_value = True
    
    result = authenticate_user("testuser", "password")
    
    assert result is not None
    assert result.username == "testuser"
    mock_get_user.assert_called_once_with("testuser")
    mock_verify.assert_called_once_with("password", "hashed_pass")


@patch('app.core.security.get_user')
def test_authenticate_user_not_found(mock_get_user):
    """Test authentication with non-existent user."""
    mock_get_user.return_value = None
    
    result = authenticate_user("nonexistent", "password")
    assert result is None


@patch('app.core.security.get_user')
@patch('app.core.security.verify_password')
def test_authenticate_user_wrong_password(mock_verify, mock_get_user):
    """Test authentication with wrong password."""
    mock_user = {
        "username": "testuser",
        "hashed_password": "hashed_pass",
        "disabled": False
    }
    mock_get_user.return_value = mock_user
    mock_verify.return_value = False
    
    result = authenticate_user("testuser", "wrong_password")
    assert result is None


@patch('app.core.security.get_user')
def test_authenticate_user_disabled(mock_get_user):
    """Test authentication with disabled user."""
    mock_user = {
        "username": "testuser",
        "hashed_password": "hashed_pass",
        "disabled": True
    }
    mock_get_user.return_value = mock_user
    
    result = authenticate_user("testuser", "password")
    assert result is None