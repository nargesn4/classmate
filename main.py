import asyncio
import websockets
import time

async def main():
    async with websockets.connect("ws://localhost:5678") as websocket:
        while 1:
            try:
                # a = readValues() #read values from a function
                # insertdata(a) #function to write values to mysql
                await websocket.send("some token to recognize that it's the db socket")
                time.sleep(20) #wait and then do it again
            except Exception as e:
                print(e)

asyncio.get_event_loop().run_until_complete(main())