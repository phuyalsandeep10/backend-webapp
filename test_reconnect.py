#!/usr/bin/env python3
"""
Test WebSocket reconnection to verify Redis pub/sub persistence
"""
import asyncio
import socketio
import json

async def test_reconnection_cycle():
    """Test multiple connect/disconnect cycles to see if Redis listener persists"""
    
    for cycle in range(3):
        print(f"\n🔄 === CYCLE {cycle + 1} ===")
        
        # Create a new Socket.IO client for each cycle
        sio = socketio.AsyncClient()
        
        @sio.event
        async def connect():
            print(f"✅ Cycle {cycle + 1}: Connected to WebSocket server")
            
        @sio.event
        async def disconnect():
            print(f"❌ Cycle {cycle + 1}: Disconnected from WebSocket server")
        
        @sio.on('*')
        async def catch_all(event, *args):
            print(f"📨 Cycle {cycle + 1}: Received event '{event}' with data: {args}")
        
        try:
            # Connect to the server with minimal auth (to trigger Redis messages)
            auth_data = {
                "token": f"test_token_{cycle}",
                "user_id": f"test_user_{cycle}",
                "organization_id": "1"  # Use org 1 to match the Redis messages we saw
            }
            
            print(f"🔌 Cycle {cycle + 1}: Connecting to WebSocket server...")
            await sio.connect('http://localhost:8000', 
                             socketio_path='/ws/sockets/socket.io',
                             auth=auth_data)
            
            # Stay connected for a moment
            print(f"⏳ Cycle {cycle + 1}: Staying connected for 2 seconds...")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ Cycle {cycle + 1}: Connection failed: {e}")
        finally:
            if sio.connected:
                print(f"🔌 Cycle {cycle + 1}: Disconnecting...")
                await sio.disconnect()
            
            # Wait between cycles
            if cycle < 2:  # Don't wait after the last cycle
                print(f"⏳ Waiting 1 second before next cycle...")
                await asyncio.sleep(1)

    print(f"\n🏁 Test completed. Check server logs for Redis listener activity.")

if __name__ == "__main__":
    asyncio.run(test_reconnection_cycle())
