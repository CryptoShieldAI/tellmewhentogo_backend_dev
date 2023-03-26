import asyncio
import websockets

async def handler(websocket, path):
    data = await websocket.recv()
    reply = f"data recieved as: {data}"
    await websocket.send(reply)

def startServer():
    start_server = websockets.serve(handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    startServer()

