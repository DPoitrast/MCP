#!/usr/bin/env python3
"""Simple web interface for the interactive MCP agent."""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests

from agent.mcp_agent import MCPAgent


class WebAgent:
    """Web-based interactive agent using MCP database."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        openai_api_key: Optional[str] = None
    ):
        self.base_url = base_url
        self.agent = MCPAgent(
            base_url=base_url,
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        # Store sessions in memory but authenticate with MCP database
        self.authenticated_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user with MCP database and return access token."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/token",
                data={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                return None
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token with MCP database and get user info."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def get_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get or create an authenticated session."""
        session_key = f"{user_id}_{session_id}"
        if session_key not in self.authenticated_sessions:
            self.authenticated_sessions[session_key] = {
                "conversation_history": [],
                "chat_mode": True,
                "user_id": user_id,
                "session_id": session_id,
                "created_at": datetime.now().isoformat()
            }
        return self.authenticated_sessions[session_key]
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        user_id: str,
        access_token: str,
        chat_mode: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Process a message in an authenticated session."""
        session = self.get_session(session_id, user_id)
        
        if not self.agent.openai_client:
            return {
                "error": "OpenAI not available. Please set OPENAI_API_KEY environment variable."
            }
        
        try:
            if chat_mode:
                # Direct chat mode
                result = self.agent.chat_with_openai(
                    user_message=message,
                    conversation_history=session["conversation_history"],
                    system_prompt="You are a helpful assistant for an MCP system. Be conversational and helpful.",
                    model="gpt-4o-mini",
                    stream=stream
                )
                
                if result.get("is_streaming"):
                    return {"stream": True, "generator": result["stream"]}
                else:
                    session["conversation_history"] = result["conversation_history"]
                    return {
                        "response": result["response"],
                        "usage": result.get("usage")
                    }
            else:
                # Smart mode - use intelligent MCP query
                result = self.agent.intelligent_mcp_query(
                    user_request=message,
                    token=access_token,
                    conversation_history=session["conversation_history"]
                )
                
                session["conversation_history"] = result["conversation_history"]
                
                response = result["response"]
                if result.get("action_taken"):
                    response += f"\n\n🔧 Executed: {result['action_taken']['tool']}"
                
                return {
                    "response": response,
                    "mcp_result": result.get("mcp_result"),
                    "action_taken": result.get("action_taken")
                }
                
        except Exception as e:
            return {"error": f"Error: {e}"}


# Global web agent instance
web_agent = WebAgent()

# FastAPI app
app = FastAPI(title="Interactive MCP Agent Web Interface")

# Security
security = HTTPBearer()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Interactive MCP Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: 50px;
        }
        .agent-message {
            background: #f1f8e9;
            margin-right: 50px;
        }
        .input-container {
            padding: 20px;
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        #sendButton {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        #sendButton:hover {
            background: #0056b3;
        }
        #sendButton:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #666;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .typing {
            font-style: italic;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Interactive MCP Agent</h1>
            <p>Chat with the AI-powered MCP agent</p>
            <div id="userInfo" style="display: none;">
                <small>Logged in as: <span id="username"></span> | 
                <button onclick="logout()" style="background: none; border: none; color: white; cursor: pointer;">Logout</button></small>
            </div>
        </div>
        
        <!-- Login Form -->
        <div id="loginForm" class="input-container" style="flex-direction: column; gap: 15px;">
            <h3 style="margin: 0; text-align: center;">Login to MCP Database</h3>
            <input type="text" id="usernameInput" placeholder="Username (johndoe)" style="width: 100%;">
            <input type="password" id="passwordInput" placeholder="Password (secret)" style="width: 100%;">
            <button id="loginButton" style="width: 100%;">Login</button>
            <small style="text-align: center; color: #666;">
                Default users: johndoe/secret or alice/wonderland
            </small>
        </div>
        
        <!-- Chat Interface (hidden until logged in) -->
        <div id="chatInterface" style="display: none;">
            <div class="chat-container" id="chatContainer">
                <div class="message agent-message">
                    <strong>🤖 Agent:</strong> Hello! I'm your interactive MCP agent connected to the same database as the CLI. I can help you with various tasks and answer questions. What would you like to know?
                </div>
            </div>
            
            <div style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                <label>
                    <input type="radio" name="mode" value="chat" checked> 💬 Chat Mode
                </label>
                <label style="margin-left: 20px;">
                    <input type="radio" name="mode" value="smart"> 🧠 Smart Mode (MCP Operations)
                </label>
            </div>
            
            <div class="status" id="status">
                Ready to chat
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Type your message here..." autofocus>
                <button id="sendButton">Send</button>
            </div>
        </div>
    </div>

    <script>
        class MCPAgent {
            constructor() {
                this.sessionId = this.generateSessionId();
                this.accessToken = null;
                this.userInfo = null;
                
                // UI elements
                this.chatContainer = document.getElementById('chatContainer');
                this.messageInput = document.getElementById('messageInput');
                this.sendButton = document.getElementById('sendButton');
                this.status = document.getElementById('status');
                this.loginForm = document.getElementById('loginForm');
                this.chatInterface = document.getElementById('chatInterface');
                this.usernameInput = document.getElementById('usernameInput');
                this.passwordInput = document.getElementById('passwordInput');
                this.loginButton = document.getElementById('loginButton');
                
                this.setupEventListeners();
                this.checkExistingAuth();
            }
            
            generateSessionId() {
                return 'session_' + Math.random().toString(36).substr(2, 9);
            }
            
            setupEventListeners() {
                // Chat events
                this.sendButton.addEventListener('click', () => this.sendMessage());
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.sendMessage();
                });
                
                // Login events
                this.loginButton.addEventListener('click', () => this.login());
                this.usernameInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.login();
                });
                this.passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.login();
                });
            }
            
            checkExistingAuth() {
                const token = localStorage.getItem('mcp_access_token');
                if (token) {
                    this.accessToken = token;
                    this.showChatInterface();
                }
            }
            
            async login() {
                const username = this.usernameInput.value.trim();
                const password = this.passwordInput.value.trim();
                
                if (!username || !password) {
                    alert('Please enter both username and password');
                    return;
                }
                
                this.loginButton.disabled = true;
                this.loginButton.textContent = 'Logging in...';
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        this.accessToken = data.access_token;
                        this.userInfo = data.user_info;
                        
                        // Store token
                        localStorage.setItem('mcp_access_token', this.accessToken);
                        
                        this.showChatInterface();
                    } else {
                        const error = await response.json();
                        alert(`Login failed: ${error.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    alert(`Login error: ${error.message}`);
                } finally {
                    this.loginButton.disabled = false;
                    this.loginButton.textContent = 'Login';
                }
            }
            
            showChatInterface() {
                this.loginForm.style.display = 'none';
                this.chatInterface.style.display = 'block';
                
                if (this.userInfo) {
                    document.getElementById('username').textContent = this.userInfo.username || 'User';
                    document.getElementById('userInfo').style.display = 'block';
                }
                
                this.messageInput.focus();
            }
            
            logout() {
                localStorage.removeItem('mcp_access_token');
                this.accessToken = null;
                this.userInfo = null;
                
                this.loginForm.style.display = 'block';
                this.chatInterface.style.display = 'none';
                document.getElementById('userInfo').style.display = 'none';
                
                // Clear form
                this.usernameInput.value = '';
                this.passwordInput.value = '';
                this.usernameInput.focus();
            }
            
            async sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message || !this.accessToken) return;
                
                // Get selected mode
                const chatMode = document.querySelector('input[name="mode"]:checked').value === 'chat';
                
                this.addMessage('user', message);
                this.messageInput.value = '';
                this.setLoading(true);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.accessToken}`
                        },
                        body: JSON.stringify({
                            session_id: this.sessionId,
                            message: message,
                            chat_mode: chatMode
                        })
                    });
                    
                    if (response.status === 401) {
                        // Token expired, need to re-login
                        this.logout();
                        alert('Session expired. Please log in again.');
                        return;
                    }
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        this.addMessage('agent', `❌ ${data.error}`, 'error');
                    } else {
                        let responseText = data.response;
                        if (data.action_taken) {
                            responseText += `\\n\\n🔧 Executed: ${data.action_taken.tool}`;
                        }
                        this.addMessage('agent', responseText);
                    }
                } catch (error) {
                    this.addMessage('agent', `❌ Network error: ${error.message}`, 'error');
                } finally {
                    this.setLoading(false);
                }
            }
            
            addMessage(sender, content, className = '') {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message ${className}`;
                
                const icon = sender === 'user' ? '👤' : '🤖';
                const label = sender === 'user' ? 'You' : 'Agent';
                
                messageDiv.innerHTML = `<strong>${icon} ${label}:</strong> ${content}`;
                
                this.chatContainer.appendChild(messageDiv);
                this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
            }
            
            setLoading(loading) {
                this.sendButton.disabled = loading;
                this.status.textContent = loading ? 'Thinking...' : 'Ready to chat';
                
                if (loading) {
                    const typingDiv = document.createElement('div');
                    typingDiv.className = 'message agent-message typing';
                    typingDiv.id = 'typing';
                    typingDiv.innerHTML = '<strong>🤖 Agent:</strong> Typing...';
                    this.chatContainer.appendChild(typingDiv);
                } else {
                    const typingDiv = document.getElementById('typing');
                    if (typingDiv) typingDiv.remove();
                }
                
                this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
            }
        }
        
        // Global functions
        function logout() {
            if (window.mcpAgent) {
                window.mcpAgent.logout();
            }
        }
        
        // Initialize the agent when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            window.mcpAgent = new MCPAgent();
        });
    </script>
</body>
</html>
"""


class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    chat_mode: bool = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: Dict[str, Any]


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token."""
    user_info = await web_agent.verify_token(credentials.credentials)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"token": credentials.credentials, "user_info": user_info}

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the web interface."""
    return HTML_TEMPLATE

@app.post("/login", response_model=AuthResponse)
async def login_endpoint(request: LoginRequest):
    """Authenticate user with MCP database."""
    try:
        access_token = await web_agent.authenticate_user(request.username, request.password)
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Get user info
        user_info = await web_agent.verify_token(access_token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        return AuthResponse(
            access_token=access_token,
            user_info=user_info
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {e}")

@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Handle authenticated chat messages."""
    try:
        user_info = current_user["user_info"]
        access_token = current_user["token"]
        
        result = await web_agent.process_message(
            session_id=request.session_id,
            message=request.message,
            user_id=str(user_info.get("id", user_info.get("username", "unknown"))),
            access_token=access_token,
            chat_mode=request.chat_mode
        )
        return result
    except Exception as e:
        return {"error": f"Internal error: {e}"}


@app.get("/status")
async def status_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get authenticated agent status."""
    user_info = current_user["user_info"]
    return {
        "status": "operational",
        "openai_available": web_agent.agent.openai_client is not None,
        "tools_available": len(web_agent.agent.get_available_tools()),
        "active_sessions": len(web_agent.authenticated_sessions),
        "user": user_info.get("username", "unknown"),
        "database_connected": True  # Since we're using the same MCP database
    }


@app.get("/tools")
async def tools_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get available MCP tools (authenticated)."""
    tools = web_agent.agent.get_available_tools()
    user_info = current_user["user_info"]
    return {
        "tools": tools,
        "count": len(tools),
        "user": user_info.get("username", "unknown")
    }


def main():
    """Run the web interface."""
    parser = argparse.ArgumentParser(description="Web interface for Interactive MCP Agent")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--mcp-url", default="http://localhost:8000", help="MCP server URL")
    parser.add_argument("--openai-key", help="OpenAI API key")
    
    args = parser.parse_args()
    
    # Initialize global web agent
    global web_agent
    web_agent = WebAgent(
        base_url=args.mcp_url,
        openai_api_key=args.openai_key
    )
    
    print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
    print(f"🔗 MCP Server: {args.mcp_url}")
    print(f"🤖 OpenAI Available: {web_agent.agent.openai_client is not None}")
    print(f"🔧 Tools Available: {len(web_agent.agent.get_available_tools())}")
    
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()