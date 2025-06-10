"""Integration tests for the complete application flow."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict


class TestUserWorkflow:
    """Test complete user workflows."""
    
    def test_user_authentication_flow(self, test_client: TestClient):
        """Test complete authentication flow."""
        # 1. Try accessing protected resource without auth
        response = test_client.get("/api/v1/herd")
        assert response.status_code == 401
        
        # 2. Get token with valid credentials
        token_response = test_client.post(
            "/api/v1/token",
            data={"username": "johndoe", "password": "secret"}
        )
        assert token_response.status_code == 200
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # 3. Use token to access protected resource
        headers = {"Authorization": f"Bearer {access_token}"}
        protected_response = test_client.get("/api/v1/herd", headers=headers)
        assert protected_response.status_code == 200
        
        # 4. Get user info
        me_response = test_client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["username"] == "johndoe"


class TestHerdWorkflow:
    """Test herd management workflows."""
    
    def test_herd_crud_operations(self, test_client: TestClient, test_user_headers: Dict[str, str]):
        """Test complete CRUD operations for herds."""
        # 1. List existing herds
        list_response = test_client.get("/api/v1/herd", headers=test_user_headers)
        assert list_response.status_code == 200
        initial_data = list_response.json()
        initial_count = initial_data["total"]
        
        # 2. Create new herd
        new_herd = {
            "name": "Integration Test Farm",
            "location": "Test Location",
            "description": "Created during integration test",
            "size": 50
        }
        create_response = test_client.post(
            "/api/v1/herd", 
            headers=test_user_headers,
            json=new_herd
        )
        assert create_response.status_code == 201
        created_herd = create_response.json()
        herd_id = created_herd["id"]
        assert created_herd["name"] == new_herd["name"]
        
        # 3. Get specific herd
        get_response = test_client.get(
            f"/api/v1/herd/{herd_id}", 
            headers=test_user_headers
        )
        assert get_response.status_code == 200
        herd_data = get_response.json()
        assert herd_data["id"] == herd_id
        assert herd_data["name"] == new_herd["name"]
        
        # 4. Update herd
        update_data = {"name": "Updated Test Farm", "size": 75}
        update_response = test_client.put(
            f"/api/v1/herd/{herd_id}",
            headers=test_user_headers,
            json=update_data
        )
        assert update_response.status_code == 200
        updated_herd = update_response.json()
        assert updated_herd["name"] == "Updated Test Farm"
        assert updated_herd["size"] == 75
        
        # 5. Verify list count increased
        list_response_after = test_client.get("/api/v1/herd", headers=test_user_headers)
        assert list_response_after.status_code == 200
        after_data = list_response_after.json()
        assert after_data["total"] == initial_count + 1
        
        # 6. Delete herd
        delete_response = test_client.delete(
            f"/api/v1/herd/{herd_id}",
            headers=test_user_headers
        )
        assert delete_response.status_code == 204
        
        # 7. Verify herd is deleted
        get_deleted_response = test_client.get(
            f"/api/v1/herd/{herd_id}", 
            headers=test_user_headers
        )
        assert get_deleted_response.status_code == 404
        
        # 8. Verify list count is back to original
        final_list_response = test_client.get("/api/v1/herd", headers=test_user_headers)
        assert final_list_response.status_code == 200
        final_data = final_list_response.json()
        assert final_data["total"] == initial_count


class TestAgentIntegration:
    """Test agent integration workflows."""
    
    def test_agent_status_and_tools(self, test_client: TestClient, test_user_headers: Dict[str, str]):
        """Test agent status and tools endpoints."""
        # 1. Check agent status
        status_response = test_client.get("/api/v1/agent/status", headers=test_user_headers)
        assert status_response.status_code in [200, 503]  # Might fail if OpenAI not configured
        
        # 2. Get agent tools
        tools_response = test_client.get("/api/v1/agent/tools", headers=test_user_headers)
        assert tools_response.status_code == 200
        tools_data = tools_response.json()
        assert "tools" in tools_data
        assert "total_count" in tools_data
        
        # 3. Get agent capabilities
        cap_response = test_client.get("/api/v1/agent/capabilities", headers=test_user_headers)
        assert cap_response.status_code == 200
        cap_data = cap_response.json()
        assert "openai_available" in cap_data
        assert "mcp_tools" in cap_data


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_404_endpoints(self, test_client: TestClient, test_user_headers: Dict[str, str]):
        """Test 404 error handling."""
        # Non-existent herd
        response = test_client.get("/api/v1/herd/99999", headers=test_user_headers)
        assert response.status_code == 404
        
        # Non-existent endpoint
        response = test_client.get("/api/v1/nonexistent", headers=test_user_headers)
        assert response.status_code == 404
    
    def test_validation_errors(self, test_client: TestClient, test_user_headers: Dict[str, str]):
        """Test validation error handling."""
        # Invalid herd data
        invalid_herd = {"name": ""}  # Empty name should fail validation
        response = test_client.post(
            "/api/v1/herd",
            headers=test_user_headers,
            json=invalid_herd
        )
        assert response.status_code == 422
    
    def test_permission_errors(self, test_client: TestClient):
        """Test permission error handling."""
        # Try to access admin endpoint without proper permissions
        response = test_client.get("/api/v1/users")
        assert response.status_code == 401