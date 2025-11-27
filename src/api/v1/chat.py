import os
import asyncio
import json
from typing import Dict, cast
from uuid import uuid4
from src.agent.transaction_agent.websocket_agent import websocket_app
from src.agent.transaction_agent.state import AgentState
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage


load_dotenv()
router = APIRouter(prefix="/chat", tags=["chat"])

# Store active sessions
active_sessions: Dict[str, dict] = {}


class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.message_queues[session_id] = asyncio.Queue()
        
        # Initialize session state
        active_sessions[session_id] = {
            "messages": [],
            "intent": "",
            "slots": {},
            "missing_slots": [],
            "tool_response": "",
            "use_tool": False,
            "pin_verified": False,
            "awaiting_pin": False,
            "awaiting_input": False,
            "current_node": None
        }
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.message_queues:
            del self.message_queues[session_id]
        if session_id in active_sessions:
            del active_sessions[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        """Send message to client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
    
    async def get_user_input(self, session_id: str, prompt: str, input_type: str = "text") -> str:
        """Request input from user via WebSocket and wait for response"""
        # Send prompt to client
        await self.send_message(session_id, {
            "type": "input_request",
            "prompt": prompt,
            "input_type": input_type  # "text" or "pin"
        })
        
        # Wait for user response from queue
        queue = self.message_queues.get(session_id)
        if queue:
            response = await queue.get()
            return response
        return ""


manager = ConnectionManager()


async def stream_agent_response(session_id: str, user_message: str):
    """Process user message through the agent and stream responses"""
    try:
        state = cast(AgentState, active_sessions[session_id])
        
        # Debug: Print current state
        print(f"\n=== Processing message: '{user_message}' ===")
        print(f"Current state - awaiting_pin: {state.get('awaiting_pin')}, pin_verified: {state.get('pin_verified')}, intent: {state.get('intent')}")
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        # Process through agent with streaming
        async for event in websocket_app.astream(state, {"recursion_limit": 100}):
            # Extract the latest messages or updates
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    # Update session state
                    for key, value in node_output.items():
                        if key in state:
                            if key == "messages" and isinstance(value, list):
                                # Messages are added via reducer, get the new ones
                                new_messages = value
                                for msg in new_messages:
                                    if isinstance(msg, AIMessage):
                                        # Skip empty messages (from confirm node with tool_calls)
                                        if msg.content and str(msg.content).strip():
                                            # Stream AI responses
                                            await manager.send_message(session_id, {
                                                "type": "message",
                                                "role": "assistant",
                                                "content": msg.content
                                            })
                                    elif hasattr(msg, 'type') and msg.type == 'tool':
                                        # Stream tool results
                                        await manager.send_message(session_id, {
                                            "type": "tool_result",
                                            "content": msg.content
                                        })
                            elif key in ["intent", "slots", "missing_slots", "pin_verified", "awaiting_pin"]:
                                state[key] = value  # type: ignore
        
        # Send completion signal
        await manager.send_message(session_id, {
            "type": "complete"
        })
        
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "message": str(e)
        })


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat with the AI agent
    
    Client should send messages in this format:
    {
        "type": "message",
        "content": "user message here"
    }
    
    Or with role specified:
    {
        "type": "message",
        "role": "user",
        "content": "1235"
    }
    
    Server will send:
    {
        "type": "message",
        "role": "assistant",
        "content": "AI response"
    }
    """
    await manager.connect(websocket, session_id)
    
    # Send welcome message
    await manager.send_message(session_id, {
        "type": "message",
        "role": "assistant",
        "content": "🤖 Hi, I'm Alat AI, what would you like to do?"
    })
    
    try:
        while True:
            # Receive message from client - handle both JSON and text
            try:
                # Try to receive as JSON first
                data = await websocket.receive_json()
            except Exception:
                # If JSON parsing fails, receive as text and wrap it
                text = await websocket.receive_text()
                if not text or text.strip() == "":
                    continue
                # Treat plain text as a message
                data = {
                    "type": "message",
                    "content": text
                }
            
            message_type = data.get("type")
            content = data.get("content", "")
            
            if message_type == "message":
                # User sent a message - process through agent
                await stream_agent_response(session_id, content)
            
            elif message_type == "ping":
                # Keep-alive ping
                await manager.send_message(session_id, {"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Client {session_id} disconnected")
    except Exception as e:
        print(f"Error in WebSocket for {session_id}: {e}")
        await manager.send_message(session_id, {
            "type": "error",
            "message": f"Server error: {str(e)}"
        })
        manager.disconnect(session_id)


@router.get("/session/new")
async def create_session():
    """Create a new chat session and return session ID"""
    session_id = str(uuid4())
    return {
        "session_id": session_id,
        "websocket_url": f"/chat/ws/{session_id}"
    }




    

