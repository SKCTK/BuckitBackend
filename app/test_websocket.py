# Run this to test your websocket connection
import asyncio
import json
import websockets

async def test_chat():
    # Connect to your websocket
    async with websockets.connect("ws://localhost:8000/ws/1") as websocket:
        print("Connected to WebSocket")
        
        # Send a message
        message = {"text": "Tell me about budgeting for a family of four"}
        await websocket.send(json.dumps(message))
        print(f"Sent: {message['text']}")
        
        # Get response
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Received: {response_data['text']}")
        
        # Send another message
        message = {"text": "What about investing for retirement?"}
        await websocket.send(json.dumps(message))
        print(f"Sent: {message['text']}")
        
        # Get response
        response = await websocket.recv()
        response_data = json.loads(response)
        print(f"Received: {response_data['text']}")

if __name__ == "__main__":
    asyncio.run(test_chat())