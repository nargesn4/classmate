import tornado.web
import tornado.websocket
import tornado.ioloop
import socket
import time
import RPi.GPIO as GPIO
from ComponentControllers.Speaker import Speaker
from ComponentControllers.RgbLed import RgbLed
from Communication.Message import *

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("website/index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    
    def simple_init(self):
        self.last = time.time()
        self.stop = False

    def open(self):
        self.simple_init()
        self.waiters.add(self)
        print("New client connected")
        self.write_message(Message(CLIENT_ID_SERVER, ACTION_CHAT, {"user": CLIENT_ID_SERVER, "message": "Connection established. "}).toJSON())
        # self.loop = tornado.ioloop.PeriodicCallback(self.check_ten_seconds, 10000, io_loop=tornado.ioloop.IOLoop.instance())
        # self.loop.start()

    def on_close(self):
        print("Client disconnected")
        self.waiters.remove(self)
        
        # speaker = Speaker(70, "/home/jessepi/classmate/Resources/Audio/Testing/demo_audio.mp3")
        # speaker.play()
        # time.sleep(5)
        # speaker.pause()
        
        # self.loop.stop()

    def on_message(self, message):
        msg = Message(None,None,None).fromJSON(message)
        # self.write_message(msg.toJSON())
        self.send_updates(msg.toJSON())
        self.last = time.time()

    @classmethod
    def send_updates(cls, chat):
        # print("Sending message", chat, "to", len(cls.waiters), "waiters")
        # logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                print("Error sending message.")
                # logging.error("Error sending message", exc_info=True)

    def check_origin(self, origin):
        return True

    # def check_ten_seconds(self):
    #     print("Just checking")
    #     if (time.time() - self.last > 10):
    #         self.write_message(Message(CLIENT_ID_SERVER, ACTION_CHAT, {"user": CLIENT_ID_SERVER, "message": "You sleeping mate?"}).toJSON())
    #         self.last = time.time()
 
application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler),
    (r'/websocket', WSHandler),
])
            
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.current().start()