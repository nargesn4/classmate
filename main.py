# sockets and threading
from multiprocessing.pool import ThreadPool
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

# env
from Data.SystemState import SystemState
from settings import APPLICATION_ROOT_DIRECTORY

# data
from tinydb import TinyDB, Query
systemDatabase = TinyDB(APPLICATION_ROOT_DIRECTORY + 'Data/system.json')

# message
from Communication.Message import *

# components
from ComponentControllers.Speaker import Speaker
from ComponentControllers.Temperature import readTemperatureInside, readHumidityInside

# co2
import mh_z19

# screen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI



THIS_CLIENT_ID = CLIENT_ID_LOGIC

#display
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

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
        self.ss = SystemState()
        systemDatabase.truncate()
        systemDatabase.drop_tables()
        # systemDatabase.insert({"temperature_outside": 0})
        # systemDatabase.insert({"humidity_outside": 0})
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.display = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
        self.display.begin()
        self.connect()
        PeriodicCallback(self.keep_alive, 10000, io_loop=self.ioloop).start()
        PeriodicCallback(self.status_update, 10000, io_loop=self.ioloop).start()
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
            if (self.ws == None):
                print("connection closed")
                break
             
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
            
            print (msg.action)
            
            if (msg.action == ACTION_CHAT):
                print(msg.client_id, msg.action, '|', msg.data["user"], ": ", msg.data["message"])
            elif (msg.action == CALLBACK_DOOR_OPENED): # If the door was opened after it's been requested to do so:
                self.ss.door_open = True
                
            elif (msg.action == CALLBACK_DOOR_CLOSED): # If the door was closed after it's been requested to do so:
                self.ss.door_open = False
                
            elif (msg.action == ACTION_ACTIVATE_DO_NOT_DISTURB):
                self.ss.do_not_disturb = True
                run_background(play_audio, self.on_complete, (80, "Resources/Audio/Testing/do_not_disturb_activated.mp3", 5))
                
            elif (msg.action == ACTION_DEACTIVATE_DO_NOT_DISTURB):
                self.ss.do_not_disturb = False
                run_background(play_audio, self.on_complete, (80, "Resources/Audio/Testing/do_not_disturb_deactivated.mp3", 5))
                
            elif (msg.action == ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE):
                self.ss.temperature_outside = msg.data["temperature"]
                #self.ss.temperature_outside -= 4 # correction of -4 degrees celcius
                self.ss.humidity_outside = msg.data["humidity"]
                
            elif (msg.action == ACTION_RICKROLL):
                print ("RICKROLLED\n")
                run_background(play_audio, self.on_complete, (80, "Resources/Audio/Testing/demo_audio.mp3", 5))
                
    def on_complete(self, res):
        _workers
        print("Test {0}".format(res))

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            msg = "Keeping connection alive."
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_ALIVE, {"user": CLIENT_ID_LOGIC, "message": msg}).toJSON())
            
    def status_update(self):
        temperature_inside = readTemperatureInside()
        if (temperature_inside):
            self.ss.temperature_inside = temperature_inside
        humidity_inside = readHumidityInside()
        if (humidity_inside):
            self.ss.humidity_inside = humidity_inside
        co2 = mh_z19.read_co2valueonly()
        if (co2):
            self.ss.co2 = co2
            self.status_screen(str(co2))
        
        ssDict = vars(self.ss)
        systemDatabase.insert(ssDict)
        # the data above should also be written to a database, for easy history / algoritmic usage and plotting.
        # should include time
        historic_data = systemDatabase.all()
        historic_data = historic_data[-50:]
        try:
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_STATUS_UPDATE, ssDict).toJSON())
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_STATUS_HISTORY, historic_data).toJSON())
        except Exception as e:
            print ("Sending status update went wrong.")
            
    def status_screen(self, systemState):
        self.display.clear((255,255,255))

        draw = self.display.draw()

        # Draw a purple rectangle with yellow outline.
        draw.rectangle((10, 155, 110, 10), outline=(255,255,0), fill=(50,205,50))

        # Draw a green rectangle with black outline.
        draw.rectangle((10, 310, 110, 165), outline=(0,0,0), fill=(50,205,50))

        # Load default font.
        font = ImageFont.load_default()
        
        draw_rotated_text(self.display.buffer, 'CO2 value!', (150, 40), 90, font, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, 'This is a line of text.', (170, 10), 90, font, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, 'smoke value: ', (150, 200), 90, font, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, value , (170, 230), 90, font, fill=(0,0,0))
        self.display.display()

if __name__ == "__main__":    
    client = Client("ws://localhost:8888/websocket", 5)