#!/usr/bin/env python3
"""
Test WebSocket client to verify Redis pub/sub integration
"""
import asyncio
import socketio
import json

async def test_websocket_connection():
    # Create a Socket.IO client
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to WebSocket server")
        
    @sio.event
    async def disconnect():
        print("❌ Disconnected from WebSocket server")
    
    @sio.on('*')
    async def catch_all(event, *args):
        print(f"📨 Received event '{event}' with data: {args}")
    
    try:
        # Connect to the server with authentication
        auth_data = {
            "token": "test_token",  # Replace with a valid token if needed
            "user_id": "test_user",
            "organization_id": "test_org"
        }
        
        print("🔌 Connecting to WebSocket server...")
        await sio.connect('http://localhost:8000', 
                         socketio_path='/ws/sockets/socket.io',
                         auth=auth_data,
                         namespaces=['/chat'])
        
        # Keep connection alive for a few seconds to see messages
        print("⏳ Waiting for messages...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        if sio.connected:
            await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
