import tornado.web
import tornado.websocket
import tornado.ioloop
import socket
import time
import RPi.GPIO as GPIO
from ComponentControllers.Speaker import Speaker
from ComponentControllers.RgbLed import RgbLed
from Communication.Message import *

from tinydb import TinyDB, Query
from settings import APPLICATION_ROOT_DIRECTORY
logDatabase = TinyDB(APPLICATION_ROOT_DIRECTORY + 'Data/logs.json')

THIS_CLIENT_ID = CLIENT_ID_SERVER

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dashboard/index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    
    def simple_init(self):
        self.last = time.time()
        self.stop = False

    def open(self):
        self.simple_init()
        self.waiters.add(self)
        print("A client connected, total:", len(self.waiters))
        self.write_message(Message(THIS_CLIENT_ID, ACTION_CHAT, {"user": THIS_CLIENT_ID, "message": "Connection established. "}).toJSON())
        # self.loop = tornado.ioloop.PeriodicCallback(self.check_ten_seconds, 10000, io_loop=tornado.ioloop.IOLoop.instance())
        # self.loop.start()

    def on_close(self):
        self.close()
        self.waiters.discard(self)
        print("A client disconnected, total:", len(self.waiters))
        # self.loop.stop()

    def on_message(self, message):
        try:
            # print (message)
            msgDictionary = json.loads(message)
            msg = Message(None,None,None).fromDictionary(msgDictionary)
        except:
            print("Message received, parsing went wrong")
            return
        
        if (msg.action == ACTION_ALIVE):
            return
        
        # print ("goign in")
        # logDatabase.insert(msgDictionary)
        # if (logDatabaseLength % 10 == 0):
        #     self.send_updates(Message(THIS_CLIENT_ID, ACTION_RICKROLL, "50 more loggings were made").toJSON())
        
        # if(msg.action == "ACTION_TEMPERATURE_MEASURED"):
            # save temperature to database
        
        # self.write_message(msg.toJSON())
        # print ("okay now what1")
        self.send_updates(msg.toJSON())
        self.last = time.time()
        # print ("okay now what2\n")

    @classmethod
    def send_updates(cls, chat):
        # print("Sending message", chat, "to", len(cls.waiters), "waiters")
        # print ("sending update")
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                print("Error sending message.")

    def check_origin(self, origin):
        return True

    # def check_ten_seconds(self):
    #     print("Just checking")
    #     if (time.time() - self.last > 10):
    #         self.write_message(Message(THIS_CLIENT_ID, ACTION_CHAT, {"user": THIS_CLIENT_ID, "message": "You sleeping mate?"}).toJSON())
    #         self.last = time.time()
 
application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path":r"dashboard/"}),
    (r'/websocket', WSHandler),
])
            
if __name__ == "__main__":
    print ("1")
    http_server = tornado.httpserver.HTTPServer(application)
    print ("2")
    http_server.listen(8888)
    print ("3")
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.current().start()
    print ("5")