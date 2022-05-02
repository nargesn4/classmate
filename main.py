import asyncio
import functools
from multiprocessing.pool import ThreadPool
import time
import tornado
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

from Communication.Message import *
from ComponentControllers.Speaker import Speaker

from settings import APPLICATION_ROOT_DIRECTORY


THIS_CLIENT_ID = CLIENT_ID_LOGIC

_workers = ThreadPool(10)

def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)
    

def play_audio(volume, file_path, duration = 5):
    speaker = Speaker(volume, file_path)
    speaker.playForTime(duration)
    return "done"
        

class Client(object):
    
    def __init__(self, url, timeout):
        self.speaker = Speaker(50, APPLICATION_ROOT_DIRECTORY + "Resources/Audio/Testing/demo_audio.mp3")
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
            
            # if (msg.client_id != THIS_CLIENT_ID):
            #     continue
            if (msg.action == ACTION_CHAT):
                print(msg.client_id, msg.action, '|', msg.data["user"], ": ", msg.data["message"])
            # elif (msg.action == ACTION_RICKROLL):
            #     run_background(play_audio, self.on_complete, (50, "Resources/Audio/Testing/demo_audio.mp3", 5))          
            #elif (msg.action == ACTION_CLOSE_DOOR): 
                # run_background(play_audio, self.on_complete, (50, "Resources/Audio/Testing/do_not_disturb_activated.mp3", 5))
            #elif (msg.action == ACTION_OPEN_DOOR): 
                # run_background(play_audio, self.on_complete, (50, "Resources/Audio/Testing/do_not_disturb_deactivated.mp3", 5))   
            else:
                print(msg.client_id, msg.action)
                
    def on_complete(self, res):
        _workers
        print("Test {0}<br/>".format(res))

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            msg = "Keeping connection alive."
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_ALIVE, {"user": CLIENT_ID_LOGIC, "message": msg}).toJSON())

if __name__ == "__main__":
    client = Client("ws://localhost:8888/websocket", 5)