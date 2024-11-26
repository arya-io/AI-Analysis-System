import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        question = input("Enter AI-related question: ")
        response = input("Enter your response to the question: ")
        
        message = f"{question}|{response}"
        await websocket.send(message)
        print(f"Client sent question and response: {message}")
        
        feedback = await websocket.recv()
        print(f"Client received feedback:\n{feedback}")

# Run the WebSocket client
if __name__ == "__main__":
    asyncio.run(send_message())
