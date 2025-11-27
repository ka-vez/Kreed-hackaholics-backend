# WebSocket Testing Guide

## Testing with Postman

### 1. Get a Session ID
**HTTP Request:**
```
GET http://localhost:8000/chat/session/new
```

Response:
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "websocket_url": "/chat/ws/123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. Connect to WebSocket
**WebSocket URL:**
```
ws://localhost:8000/chat/ws/{session_id}
```

Replace `{session_id}` with the ID from step 1.

### 3. Send Messages

**User Message:**
```json
{
  "type": "message",
  "content": "I want to transfer 2000 naira to 2064350220, kuda bank"
}
```

**Input Response (for PIN, confirmations):**
```json
{
  "type": "input_response",
  "content": "1235"
}
```

**Keep-Alive Ping:**
```json
{
  "type": "ping"
}
```

### 4. Receive Messages

**AI Response:**
```json
{
  "type": "message",
  "role": "assistant",
  "content": "Sure thing. You are about to transfer N2,000 to 2064350220 Kuda Bank. Is this correct?"
}
```

**Input Request (AI asking for info):**
```json
{
  "type": "input_request",
  "prompt": "Enter PIN",
  "input_type": "pin"
}
```

**Tool Result:**
```json
{
  "type": "tool_result",
  "content": "✅ N2000 Transfer to Adegbite David - Kuda bank Successful"
}
```

**Completion Signal:**
```json
{
  "type": "complete"
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Example Conversation Flow

1. **Client connects** → Receives welcome message
2. **Client sends:** `{"type": "message", "content": "transfer 1000 to 2064350220"}`
3. **Server asks:** Missing bank name
4. **Client sends:** `{"type": "message", "content": "kuda bank"}`
5. **Server confirms:** "You are about to transfer N1,000..."
6. **Client sends:** `{"type": "message", "content": "yes"}`
7. **Server requests:** PIN input
8. **Client sends:** `{"type": "input_response", "content": "1235"}`
9. **Server executes:** Tool call
10. **Server sends:** Success message
11. **Server sends:** `{"type": "complete"}`

## Testing Scenarios

### Scenario 1: Simple Transfer
```json
{"type": "message", "content": "transfer 2000 naira to 2064350220, kuda bank"}
```

### Scenario 2: Buy Airtime
```json
{"type": "message", "content": "buy 500 naira MTN airtime for 08012345678"}
```

### Scenario 3: General Question
```json
{"type": "message", "content": "what is wema bank?"}
```

### Scenario 4: Incomplete Info (triggers clarification)
```json
{"type": "message", "content": "I want to transfer money"}
```

## Python Test Client

```python
import asyncio
import websockets
import json

async def test_chat():
    # Get session
    import requests
    response = requests.get("http://localhost:8000/chat/session/new")
    session_id = response.json()["session_id"]
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/chat/ws/{session_id}"
    
    async with websockets.connect(uri) as websocket:
        # Receive welcome message
        welcome = await websocket.recv()
        print(f"< {welcome}")
        
        # Send a message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "transfer 1000 to 2064350220, kuda bank"
        }))
        
        # Receive responses
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"< {data}")
            
            if data.get("type") == "complete":
                break
            
            # Handle input requests
            if data.get("type") == "input_request":
                # Send confirmation or PIN
                await websocket.send(json.dumps({
                    "type": "input_response",
                    "content": "yes" if "confirm" in data.get("prompt", "").lower() else "1235"
                }))

if __name__ == "__main__":
    asyncio.run(test_chat())
```

## Running the Server

```bash
uvicorn src.main:app --reload
```

Server will be available at: `http://localhost:8000`
WebSocket endpoint: `ws://localhost:8000/chat/ws/{session_id}`
