import asyncio
import websockets
import json
import sys

async def test_voice_cmd(cmd):
    uri = "ws://127.0.0.1:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            payload = {"command": cmd}
            await websocket.send(json.dumps(payload))
            print(f"Sent voice command: {cmd}")
            
            # Wait for responses
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    msg_type = data.get("type", "unknown")
                    if msg_type == "greeting" or msg_type == "health_update":
                        continue
                        
                    print(f"[{msg_type.upper()}] {data.get('text', '')}")
                    if msg_type == "response":
                        print(f"Final Response: {data.get('text', '')}")
                        break
                except asyncio.TimeoutError:
                    print("Timeout waiting for response. Execution might be taking longer.")
                    break
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    cmd = "System status batao" if len(sys.argv) == 1 else " ".join(sys.argv[1:])
    asyncio.run(test_voice_cmd(cmd))
