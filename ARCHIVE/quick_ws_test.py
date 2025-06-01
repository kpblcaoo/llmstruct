#!/usr/bin/env python3
"""
Quick WebSocket Test Script
"""

import asyncio
import json
import websockets
import sys

async def test_websocket():
    """Test WebSocket with automatic messages"""
    
    session_id = sys.argv[1] if len(sys.argv) > 1 else "test-session"
    url = f"ws://localhost:8000/api/v1/chat/ws?session_id={session_id}&api_key=dev-key"
    
    print(f"🔗 Testing WebSocket: {url}")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected!")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            print(f"📨 Welcome: {json.loads(welcome)}")
            
            # Send test messages
            test_messages = [
                "Привет! Как дела?",
                "Расскажи о возможностях WebSocket чата",
                "quit"
            ]
            
            for msg_text in test_messages:
                if msg_text == "quit":
                    break
                    
                message = {
                    "message": msg_text,
                    "context_mode": "focused"
                }
                
                print(f"💬 Sending: {msg_text}")
                await websocket.send(json.dumps(message))
                
                # Wait for response
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if data.get("type") == "message":
                        print(f"🤖 AI: {data.get('content')[:100]}...")
                        print(f"   📝 Provider: {data.get('context_used', {}).get('provider_used', 'unknown')}")
                        break
                    elif data.get("type") == "typing":
                        print("⌨️  AI is typing...")
                    else:
                        print(f"📨 {data.get('type')}: {data}")
                        
                await asyncio.sleep(1)
            
            print("✅ WebSocket test completed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 