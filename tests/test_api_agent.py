"""Test agent API endpoints."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict
from unittest.mock import patch, Mock


def test_agent_status(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test agent status endpoint."""
    response = test_client.get("/api/v1/agent/status", headers=test_user_headers)
    # This might fail if OpenAI key is not configured, but should return proper error
    assert response.status_code in [200, 503]


def test_agent_tools(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test agent tools listing endpoint."""
    response = test_client.get("/api/v1/agent/tools", headers=test_user_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert "total_count" in data
    assert isinstance(data["tools"], list)


def test_agent_capabilities(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test agent capabilities endpoint."""
    response = test_client.get("/api/v1/agent/capabilities", headers=test_user_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "openai_available" in data
    assert "mcp_tools" in data
    assert "agent_info" in data
    assert isinstance(data["openai_available"], bool)
    assert isinstance(data["mcp_tools"], list)
    assert isinstance(data["agent_info"], dict)


@patch('agent.mcp_agent.MCPAgent.chat_with_openai')
def test_agent_chat_success(mock_chat, test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test successful agent chat."""
    mock_chat.return_value = {
        "response": "Hello! How can I help you?",
        "conversation_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you?"}
        ],
        "usage": {"total_tokens": 25}
    }
    
    response = test_client.post(
        "/api/v1/agent/chat",
        headers=test_user_headers,
        json={
            "message": "Hello",
            "model": "gpt-3.5-turbo"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_history" in data
    assert data["response"] == "Hello! How can I help you?"


@patch('agent.mcp_agent.MCPAgent.intelligent_mcp_query')
def test_agent_query_success(mock_query, test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test successful intelligent query."""
    mock_query.return_value = {
        "response": "I found 5 animals in your herd.",
        "conversation_history": [
            {"role": "user", "content": "How many animals do I have?"},
            {"role": "assistant", "content": "I found 5 animals in your herd."}
        ],
        "mcp_result": {"count": 5},
        "action_taken": {"operation": "list_herd"}
    }
    
    response = test_client.post(
        "/api/v1/agent/query",
        headers=test_user_headers,
        json={"request": "How many animals do I have?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_history" in data
    assert "mcp_result" in data
    assert "action_taken" in data


def test_agent_chat_missing_message(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test chat endpoint with missing message."""
    response = test_client.post(
        "/api/v1/agent/chat",
        headers=test_user_headers,
        json={"model": "gpt-3.5-turbo"}
    )
    
    assert response.status_code == 422  # Validation error


def test_agent_query_missing_request(test_client: TestClient, test_user_headers: Dict[str, str]):
    """Test query endpoint with missing request."""
    response = test_client.post(
        "/api/v1/agent/query",
        headers=test_user_headers,
        json={}
    )
    
    assert response.status_code == 422  # Validation error


def test_agent_endpoints_unauthorized(test_client: TestClient):
    """Test agent endpoints without authorization."""
    endpoints = [
        "/api/v1/agent/status",
        "/api/v1/agent/tools", 
        "/api/v1/agent/capabilities"
    ]
    
    for endpoint in endpoints:
        response = test_client.get(endpoint)
        assert response.status_code == 401
    
    # Test POST endpoints
    post_endpoints = [
        ("/api/v1/agent/chat", {"message": "test"}),
        ("/api/v1/agent/query", {"request": "test"})
    ]
    
    for endpoint, data in post_endpoints:
        response = test_client.post(endpoint, json=data)
        assert response.status_code == 401