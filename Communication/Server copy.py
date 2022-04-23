import asyncio
from concurrent.futures.thread import _worker
import socket
import tornado.ioloop
import tornado.websocket


tornado.ioloop.IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")
io_loop = tornado.ioloop.IOLoop.current()
asyncio.set_event_loop(io_loop.asyncio_loop)

clients = []

def bcint(message):
    for client in clients:
        client.write_message(message)
        print("broadcasted")

def Broadcast(message):
    io_loop.asyncio_loop.call_soon_threadsafe(bcint, message)

_worker.broadcast = Broadcast

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('new connection')
        clients.append(self)
      
    def on_message(self, message):
        print('message received:  %s' % message)
        response = asyncio.Handle.HandleRequest(message, self.write_message)
 
    def on_close(self):
        print('connection closed')
        clients.remove(self)
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8765)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.current().start()