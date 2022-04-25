import time
import tornado
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

from Communication.Message import *

class Client(object):
    
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.connect()
        PeriodicCallback(self.keep_alive, 10000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print("Connecting...")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            print("connection error")
        else:
            # print("connected")
            self.run()

    @gen.coroutine
    def run(self):
        once = False
        while True:
            msgStr = yield self.ws.read_message()
            # print (msgStr)
            try:
                msg = Message(None, None, None).fromJSON(msgStr)
            except:
                print("Unable to deserialize message.")
                self.ws = None
                continue
            
            if msg is None:
                print("connection closed")
                self.ws = None
                break
            
            # if (msg.client_id != CLIENT_ID_LOGIC):
            #     continue
            if (msg.action == ACTION_CHAT):
                print(msg.client_id, msg.action, '|', msg.data["user"], ": ", msg.data["message"])
            else:
                print(msg.client_id, msg.action)
            

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            msg = "Keeping connection alive."
            self.ws.write_message(Message(CLIENT_ID_LOGIC, ACTION_ALIVE, {"user": CLIENT_ID_LOGIC, "message": msg}).toJSON())

if __name__ == "__main__":
    client = Client("ws://localhost:8888/websocket", 5)