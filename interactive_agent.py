#!/usr/bin/env python3
"""Interactive MCP Agent with OpenAI integration."""

import os
import sys
import json
import asyncio
import readline
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.mcp_agent import MCPAgent


class InteractiveAgent:
    """Interactive agent with conversation management and commands."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        openai_api_key: Optional[str] = None,
        username: str = "johndoe",
        password: str = "secret",
        enable_streaming: bool = True
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.conversation_history: List[Dict[str, str]] = []
        self.session_data: Dict[str, Any] = {}
        self.access_token: Optional[str] = None
        self.enable_streaming = enable_streaming
        self.session_file = os.path.expanduser('~/.mcp_agent_session.json')
        
        # Initialize the agent
        self.agent = MCPAgent(
            base_url=base_url,
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Setup readline for better input handling
        self._setup_readline()
        
        # Available commands
        self.commands = {
            '/help': self._cmd_help,
            '/quit': self._cmd_quit,
            '/exit': self._cmd_quit,
            '/clear': self._cmd_clear,
            '/history': self._cmd_history,
            '/login': self._cmd_login,
            '/tools': self._cmd_tools,
            '/status': self._cmd_status,
            '/save': self._cmd_save,
            '/load': self._cmd_load,
            '/execute': self._cmd_execute,
            '/chat': self._cmd_chat_mode,
            '/smart': self._cmd_smart_mode,
            '/stream': self._cmd_toggle_streaming,
            '/session': self._cmd_session_info,
        }
        
        self.chat_mode = True  # Default to chat mode
        
        # Load previous session if available
        self._load_session()
        
    def _setup_readline(self):
        """Setup readline for command history and completion."""
        try:
            # Enable tab completion
            readline.parse_and_bind('tab: complete')
            
            # Set completion function
            readline.set_completer(self._completer)
            
            # Load history if it exists
            history_file = os.path.expanduser('~/.mcp_agent_history')
            if os.path.exists(history_file):
                readline.read_history_file(history_file)
                
        except Exception:
            # If readline is not available, continue without it
            pass
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for commands and tools."""
        options = []
        
        if text.startswith('/'):
            # Command completion
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        else:
            # Tool name completion
            tools = self.agent.get_available_tools()
            tool_names = [tool.get('name', '') for tool in tools]
            options = [name for name in tool_names if name.startswith(text)]
        
        try:
            return options[state]
        except IndexError:
            return None
    
    def _save_history(self):
        """Save command history."""
        try:
            history_file = os.path.expanduser('~/.mcp_agent_history')
            readline.write_history_file(history_file)
        except Exception:
            pass
    
    def _load_session(self):
        """Load previous session data."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Restore conversation history if recent (within 24 hours)
                timestamp = session_data.get('timestamp')
                if timestamp:
                    session_time = datetime.fromisoformat(timestamp)
                    if (datetime.now() - session_time).total_seconds() < 86400:  # 24 hours
                        self.conversation_history = session_data.get('conversation_history', [])
                        self.session_data = session_data.get('session_data', {})
                        
        except Exception:
            # If loading fails, start fresh
            pass
    
    def _save_session(self):
        """Save current session data."""
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'conversation_history': self.conversation_history,
                'session_data': self.session_data,
                'chat_mode': self.chat_mode,
                'enable_streaming': self.enable_streaming
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception:
            pass
    
    async def _get_access_token(self) -> bool:
        """Get access token for authentication."""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/token",
                data={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                print(f"✓ Logged in as {self.username}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def _print_welcome(self):
        """Print welcome message."""
        print("🤖 Interactive MCP Agent")
        print("=" * 50)
        print(f"Connected to: {self.base_url}")
        print(f"OpenAI Available: {'✓' if self.agent.openai_client else '❌'}")
        print(f"MCP Tools: {len(self.agent.get_available_tools())}")
        print()
        print("Type '/help' for commands or just start chatting!")
        print("Use '/quit' to exit")
        print("-" * 50)
    
    def _cmd_help(self, args: str = "") -> str:
        """Show help information."""
        help_text = """
🤖 Interactive MCP Agent Commands:

CONVERSATION:
  /chat             - Switch to chat mode (talk to OpenAI)
  /smart            - Switch to smart mode (AI + MCP operations)
  /stream           - Toggle streaming responses
  /clear            - Clear conversation history
  /history          - Show conversation history

MCP OPERATIONS:
  /tools            - List available MCP tools
  /execute <tool>   - Execute an MCP tool
  /status           - Show agent status

SESSION MANAGEMENT:
  /session          - Show session information
  /login            - Re-authenticate with the server
  /save <file>      - Save conversation to file
  /load <file>      - Load conversation from file

SYSTEM:
  /help             - Show this help
  /quit, /exit      - Exit the agent

MODES:
- Chat Mode (💬): Direct conversation with OpenAI
- Smart Mode (🧠): AI interprets requests and executes MCP operations

FEATURES:
- 📡 Streaming: Real-time response streaming (toggle with /stream)
- 💾 Auto-save: Sessions automatically saved and restored
- 🔄 Tab completion: Command and tool name completion

Just type normally to chat with the agent!
"""
        return help_text.strip()
    
    def _cmd_quit(self, args: str = "") -> str:
        """Quit the interactive agent."""
        self._save_history()
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    def _cmd_clear(self, args: str = "") -> str:
        """Clear conversation history."""
        self.conversation_history = []
        return "✓ Conversation history cleared"
    
    def _cmd_history(self, args: str = "") -> str:
        """Show conversation history."""
        if not self.conversation_history:
            return "No conversation history"
        
        history_text = "\n📋 Conversation History:\n" + "-" * 30 + "\n"
        for i, msg in enumerate(self.conversation_history):
            role = msg['role'].capitalize()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            history_text += f"{i+1}. {role}: {content}\n"
        
        return history_text
    
    async def _cmd_login(self, args: str = "") -> str:
        """Re-authenticate with the server."""
        if await self._get_access_token():
            return "✓ Successfully re-authenticated"
        else:
            return "❌ Authentication failed"
    
    def _cmd_tools(self, args: str = "") -> str:
        """List available MCP tools."""
        tools = self.agent.get_available_tools()
        
        tools_text = f"\n🔧 Available MCP Tools ({len(tools)} total):\n" + "-" * 40 + "\n"
        
        for tool in tools[:20]:  # Show first 20 tools
            name = tool.get('name', 'Unknown')
            desc = tool.get('description', 'No description')
            tools_text += f"• {name}\n  {desc}\n\n"
        
        if len(tools) > 20:
            tools_text += f"... and {len(tools) - 20} more tools\n"
        
        return tools_text
    
    def _cmd_status(self, args: str = "") -> str:
        """Show agent status."""
        status = {
            "Agent": "✓ Active",
            "OpenAI": "✓ Connected" if self.agent.openai_client else "❌ Not connected",
            "MCP Server": self.base_url,
            "Authentication": "✓ Logged in" if self.access_token else "❌ Not logged in",
            "Tools Available": len(self.agent.get_available_tools()),
            "Conversation Messages": len(self.conversation_history),
            "Mode": "Smart Mode" if not self.chat_mode else "Chat Mode"
        }
        
        status_text = "\n📊 Agent Status:\n" + "-" * 20 + "\n"
        for key, value in status.items():
            status_text += f"{key}: {value}\n"
        
        return status_text
    
    def _cmd_save(self, args: str = "") -> str:
        """Save conversation to file."""
        filename = args.strip() or f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "conversation_history": self.conversation_history,
                "session_data": self.session_data
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return f"✓ Conversation saved to {filename}"
        except Exception as e:
            return f"❌ Failed to save: {e}"
    
    def _cmd_load(self, args: str = "") -> str:
        """Load conversation from file."""
        filename = args.strip()
        if not filename:
            return "❌ Please specify a filename"
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.conversation_history = data.get("conversation_history", [])
            self.session_data = data.get("session_data", {})
            
            return f"✓ Conversation loaded from {filename} ({len(self.conversation_history)} messages)"
        except Exception as e:
            return f"❌ Failed to load: {e}"
    
    async def _cmd_execute(self, args: str = "") -> str:
        """Execute an MCP tool directly."""
        if not args:
            return "❌ Please specify a tool name"
        
        if not self.access_token:
            if not await self._get_access_token():
                return "❌ Authentication required"
        
        try:
            tool_name = args.strip()
            result = self.agent.execute_operation(tool_name, self.access_token)
            return f"✓ Tool executed successfully:\n{json.dumps(result, indent=2)}"
        except Exception as e:
            return f"❌ Tool execution failed: {e}"
    
    def _cmd_chat_mode(self, args: str = "") -> str:
        """Switch to chat mode."""
        self.chat_mode = True
        return "✓ Switched to Chat Mode - Direct conversation with OpenAI"
    
    def _cmd_smart_mode(self, args: str = "") -> str:
        """Switch to smart mode."""
        self.chat_mode = False
        return "✓ Switched to Smart Mode - AI will execute MCP operations"
    
    def _cmd_toggle_streaming(self, args: str = "") -> str:
        """Toggle streaming mode."""
        self.enable_streaming = not self.enable_streaming
        status = "enabled" if self.enable_streaming else "disabled"
        return f"✓ Streaming {status}"
    
    def _cmd_session_info(self, args: str = "") -> str:
        """Show session information."""
        session_info = f"""
📱 Session Information:
- Messages in history: {len(self.conversation_history)}
- Mode: {'Chat' if self.chat_mode else 'Smart'}
- Streaming: {'enabled' if self.enable_streaming else 'disabled'}
- Session file: {self.session_file}
- Auto-save: enabled
        """
        return session_info.strip()
    
    async def _process_command(self, user_input: str) -> str:
        """Process a command."""
        parts = user_input.split(' ', 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            cmd_func = self.commands[command]
            if asyncio.iscoroutinefunction(cmd_func):
                return await cmd_func(args)
            else:
                return cmd_func(args)
        else:
            return f"❌ Unknown command: {command}. Type '/help' for available commands."
    
    async def _process_conversation(self, user_input: str):
        """Process a conversation message with streaming support."""
        if not self.agent.openai_client:
            return "❌ OpenAI not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            if self.chat_mode:
                # Direct chat with OpenAI
                result = self.agent.chat_with_openai(
                    user_message=user_input,
                    conversation_history=self.conversation_history,
                    system_prompt="You are a helpful assistant for an MCP (Model Context Protocol) system. Be conversational and helpful.",
                    stream=self.enable_streaming
                )
                
                if result.get("is_streaming") and self.enable_streaming:
                    # Handle streaming response
                    print("🤖 Agent: ", end="", flush=True)
                    full_response = ""
                    
                    try:
                        for chunk in result["stream"]:
                            print(chunk, end="", flush=True)
                            full_response += chunk
                        print()  # New line after streaming
                        
                        # Update conversation history manually since streaming doesn't do it automatically
                        self.conversation_history.append({"role": "user", "content": user_input})
                        self.conversation_history.append({"role": "assistant", "content": full_response})
                        
                        return None  # Indicate streaming was handled
                        
                    except Exception as e:
                        print(f"\n❌ Streaming error: {e}")
                        return f"❌ Streaming error: {e}"
                else:
                    # Non-streaming response
                    self.conversation_history = result["conversation_history"]
                    return result["response"]
            
            else:
                # Smart mode - AI + MCP operations (no streaming for now)
                if not self.access_token:
                    await self._get_access_token()
                
                if not self.access_token:
                    return "❌ Authentication required for MCP operations"
                
                result = self.agent.intelligent_mcp_query(
                    user_request=user_input,
                    token=self.access_token,
                    conversation_history=self.conversation_history
                )
                
                self.conversation_history = result["conversation_history"]
                
                response = result["response"]
                if result.get("action_taken"):
                    response += f"\n\n🔧 Executed: {result['action_taken']['tool']}"
                
                return response
                
        except Exception as e:
            return f"❌ Error: {e}"
    
    async def run(self):
        """Run the interactive agent."""
        self._print_welcome()
        
        # Try to authenticate
        if not await self._get_access_token():
            print("⚠️  Authentication failed - some features may be limited")
        
        print()
        
        try:
            while True:
                try:
                    # Show current mode in prompt
                    mode_indicator = "💬" if self.chat_mode else "🧠"
                    stream_indicator = "📡" if self.enable_streaming else ""
                    user_input = input(f"{mode_indicator}{stream_indicator} You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Process commands or conversation
                    if user_input.startswith('/'):
                        response = await self._process_command(user_input)
                        print(f"🤖 Agent: {response}")
                    else:
                        response = await self._process_conversation(user_input)
                        # Only print response if it wasn't handled by streaming
                        if response is not None:
                            print(f"🤖 Agent: {response}")
                    
                    print()
                    
                    # Auto-save session periodically
                    self._save_session()
                    
                except KeyboardInterrupt:
                    print("\n\nUse '/quit' to exit gracefully.")
                    continue
                except EOFError:
                    break
                    
        finally:
            self._save_history()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Interactive MCP Agent with OpenAI")
    parser.add_argument("--url", default="http://localhost:8000", help="MCP server URL")
    parser.add_argument("--username", default="johndoe", help="Username for authentication")
    parser.add_argument("--password", default="secret", help="Password for authentication")
    parser.add_argument("--openai-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    
    args = parser.parse_args()
    
    agent = InteractiveAgent(
        base_url=args.url,
        openai_api_key=args.openai_key,
        username=args.username,
        password=args.password
    )
    
    await agent.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)