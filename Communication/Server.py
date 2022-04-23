import tornado.web
import tornado.websocket
import tornado.ioloop
import socket
import time
import RPi.GPIO as GPIO

import sys
sys.path.append('../ComponentControllers')
from Speaker import Speaker
from RgbLed import RgbLed

class WSHandler(tornado.websocket.WebSocketHandler):
    def simple_init(self):
        self.last = time.time()
        self.stop = False

    def open(self):
        self.simple_init()
        print("New client connected")
        self.write_message("You are connected")
        self.loop = tornado.ioloop.PeriodicCallback(self.check_ten_seconds, 10000, io_loop=tornado.ioloop.IOLoop.instance())
        self.loop.start()

    def on_message(self, message):
        self.write_message(u"You said: " + message)
        self.last = time.time()

    def on_close(self):
        print("Client disconnected")
        speaker = Speaker(70, "/home/jessepi/classmate/Resources/Audio/Testing/demo_audio.mp3")
        GPIO.setmode(GPIO.BCM)
        led = RgbLed(22, 27, 17)
        led.doNotDisturb()
        speaker.play()
        time.sleep(5)
        speaker.pause()
        self.loop.stop()

    def check_origin(self, origin):
        return True

    def check_ten_seconds(self):
        print("Just checking")
        if (time.time() - self.last > 10):
            self.write_message("You sleeping mate?")
            self.last = time.time()
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
            
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8765)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.current().start()