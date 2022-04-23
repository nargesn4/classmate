import Communication.Server
import tornado
import settings
import databases
import threading

settings.init()
databases.init()

if __name__ == "__main__":
    app = Communication.Server.make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    