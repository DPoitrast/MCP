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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.mcp_agent import MCPAgent


class WebAgent:
    """Web-based interactive agent."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        openai_api_key: Optional[str] = None
    ):
        self.agent = MCPAgent(
            base_url=base_url,
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "conversation_history": [],
                "chat_mode": True,
                "created_at": datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        stream: bool = False
    ) -> Dict[str, Any]:
        """Process a message in a session."""
        session = self.get_session(session_id)
        
        if not self.agent.openai_client:
            return {
                "error": "OpenAI not available. Please set OPENAI_API_KEY environment variable."
            }
        
        try:
            result = self.agent.chat_with_openai(
                user_message=message,
                conversation_history=session["conversation_history"],
                system_prompt="You are a helpful assistant for an MCP system. Be conversational and helpful.",
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
                
        except Exception as e:
            return {"error": f"Error: {e}"}


# Global web agent instance
web_agent = WebAgent()

# FastAPI app
app = FastAPI(title="Interactive MCP Agent Web Interface")

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
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message agent-message">
                <strong>🤖 Agent:</strong> Hello! I'm your interactive MCP agent. I can help you with various tasks and answer questions. What would you like to know?
            </div>
        </div>
        
        <div class="status" id="status">
            Ready to chat
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message here..." autofocus>
            <button id="sendButton">Send</button>
        </div>
    </div>

    <script>
        class MCPAgent {
            constructor() {
                this.sessionId = this.generateSessionId();
                this.chatContainer = document.getElementById('chatContainer');
                this.messageInput = document.getElementById('messageInput');
                this.sendButton = document.getElementById('sendButton');
                this.status = document.getElementById('status');
                
                this.setupEventListeners();
            }
            
            generateSessionId() {
                return 'session_' + Math.random().toString(36).substr(2, 9);
            }
            
            setupEventListeners() {
                this.sendButton.addEventListener('click', () => this.sendMessage());
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.sendMessage();
                });
            }
            
            async sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message) return;
                
                this.addMessage('user', message);
                this.messageInput.value = '';
                this.setLoading(true);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            session_id: this.sessionId,
                            message: message
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.error) {
                        this.addMessage('agent', `❌ ${data.error}`, 'error');
                    } else {
                        this.addMessage('agent', data.response);
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
        
        // Initialize the agent when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new MCPAgent();
        });
    </script>
</body>
</html>
"""


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the web interface."""
    return HTML_TEMPLATE


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat messages."""
    try:
        result = await web_agent.process_message(
            session_id=request.session_id,
            message=request.message
        )
        return result
    except Exception as e:
        return {"error": f"Internal error: {e}"}


@app.get("/status")
async def status_endpoint():
    """Get agent status."""
    return {
        "status": "operational",
        "openai_available": web_agent.agent.openai_client is not None,
        "tools_available": len(web_agent.agent.get_available_tools()),
        "active_sessions": len(web_agent.sessions)
    }


@app.get("/tools")
async def tools_endpoint():
    """Get available tools."""
    tools = web_agent.agent.get_available_tools()
    return {
        "tools": tools,
        "count": len(tools)
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