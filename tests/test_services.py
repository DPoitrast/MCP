"""Test service layer components."""

import pytest
from unittest.mock import Mock, patch
from app.services.user import user_service
from app.services.herd import herd_service


class TestUserService:
    """Test user service."""
    
    def test_get_user_exists(self):
        """Test getting existing user."""
        user = user_service.get_user("johndoe")
        assert user is not None
        assert user["username"] == "johndoe"
        assert "email" in user
        assert "hashed_password" in user
    
    def test_get_user_not_exists(self):
        """Test getting non-existent user."""
        user = user_service.get_user("nonexistent")
        assert user is None
    
    def test_get_all_users(self):
        """Test getting all users."""
        users = user_service.get_all_users()
        assert isinstance(users, list)
        assert len(users) >= 2  # From seed data
        
        usernames = [user["username"] for user in users]
        assert "johndoe" in usernames
        assert "alice" in usernames


class TestHerdService:
    """Test herd service."""
    
    @patch('app.services.herd.herd_repository')
    def test_get_herds(self, mock_repo):
        """Test getting herds with pagination."""
        mock_herds = [
            Mock(id=1, name="Farm 1"),
            Mock(id=2, name="Farm 2")
        ]
        mock_repo.get_all.return_value = mock_herds
        mock_repo.count.return_value = 2
        
        result = herd_service.get_herds(skip=0, limit=10)
        
        assert "items" in result
        assert "total" in result
        assert "skip" in result
        assert "limit" in result
        assert result["total"] == 2
        assert len(result["items"]) == 2
        
        mock_repo.get_all.assert_called_once_with(skip=0, limit=10)
        mock_repo.count.assert_called_once()
    
    @patch('app.services.herd.herd_repository')
    def test_get_herd_by_id(self, mock_repo):
        """Test getting herd by ID."""
        mock_herd = Mock(id=1, name="Test Farm")
        mock_repo.get_by_id.return_value = mock_herd
        
        result = herd_service.get_herd_by_id(1)
        assert result == mock_herd
        mock_repo.get_by_id.assert_called_once_with(1)
    
    @patch('app.services.herd.herd_repository')
    def test_create_herd(self, mock_repo):
        """Test creating a new herd."""
        mock_herd = Mock(id=3, name="New Farm")
        mock_repo.create.return_value = mock_herd
        
        herd_data = {
            "name": "New Farm",
            "location": "Test Location",
            "size": 100
        }
        
        result = herd_service.create_herd(herd_data)
        assert result == mock_herd
        mock_repo.create.assert_called_once_with(herd_data)
    
    @patch('app.services.herd.herd_repository')
    def test_update_herd(self, mock_repo):
        """Test updating a herd."""
        mock_herd = Mock(id=1, name="Updated Farm")
        mock_repo.update.return_value = mock_herd
        
        update_data = {"name": "Updated Farm"}
        
        result = herd_service.update_herd(1, update_data)
        assert result == mock_herd
        mock_repo.update.assert_called_once_with(1, update_data)
    
    @patch('app.services.herd.herd_repository')
    def test_delete_herd(self, mock_repo):
        """Test deleting a herd."""
        mock_repo.delete.return_value = True
        
        result = herd_service.delete_herd(1)
        assert result is True
        mock_repo.delete.assert_called_once_with(1)