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

# gas (smoke)
from gas_detection import GasDetection

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
        print ("Setting up Gas Detection...")
        self.gas_detection = GasDetection()
        print ("Setting up TFT screen...")
        self.display = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
        self.display.begin()
        self.status_screen()
        print ("Connecting to WebSocket Server...")
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
            # self.status_screen(str(co2))
        ppm = self.gas_detection.percentage()
        if (ppm):
            self.ss.co = ppm[self.gas_detection.CO_GAS] * 1000
            self.ss.smoke = ppm[self.gas_detection.SMOKE_GAS] * 1000
            print (self.ss)
            # print('CO: {} ppm'.format(ppm[self.gas_detection.CO_GAS]))
            # print('H2: {} ppm'.format(ppm[self.gas_detection.H2_GAS]))
            # print('CH4: {} ppm'.format(ppm[self.gas_detection.CH4_GAS]))
            # print('LPG: {} ppm'.format(ppm[self.gas_detection.LPG_GAS]))
            # print('PROPANE: {} ppm'.format(ppm[self.gas_detection.PROPANE_GAS]))
            # print('ALCOHOL: {} ppm'.format(ppm[self.gas_detection.ALCOHOL_GAS]))
            # print('SMOKE: {} ppm\n'.format(ppm[self.gas_detection.SMOKE_GAS]))
        
        self.status_screen()
        
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
            
    def status_screen(self):
        self.display.clear((255,255,255))

        draw = self.display.draw()

        # Draw a green rectangle with black outline.
        draw.rectangle((0, 320, 240, 90), outline=(0,0,0), fill=(50,205,50))

        # Draw a purple rectangle with yellow outline.
        # draw.rectangle((10, 155, 110, 10), outline=(255,255,0), fill=(50,205,50))

        # Load default font.
        titleFont = ImageFont.truetype("arial.ttf", 40)
        subTitleFont = ImageFont.truetype("arial.ttf", 16)
        text = ImageFont.truetype("arial.ttf", 12)
        
        index = "Temperature Inside\n"
        index += "Temperature Outside\n"
        index += "Humidity Inside\n"
        index += "Humidity Outside\n"
        index += "CO2 Concentration\n"
        index += "CO Concentration\n"
        index += "Smoke Concentration\n"
        index += "Door\n"
        index += "Mode\n"
        index += "Noisy outside?\n"
        index += "Class used in 15 min?\n"
        index += "Favorable conditions?"
        
        values = str(self.ss.temperature_inside) + "°C\n"
        values += str(self.ss.temperature_outside) + "°C\n"
        values += str(self.ss.humidity_inside) + "%\n"
        values += str(self.ss.humidity_outside) + "%\n"
        values += str(self.ss.co2) + " ppm\n"
        values += str("{:.4f} ppm".format(self.ss.co / 1000)) + "\n"
        values += str("{:.4f} ppm".format(self.ss.smoke / 1000)) + "\n"
        if (self.ss.door_open == None):
            values += "Unknown\n"
        else:
            values += str(("Closed","Open")[self.ss.door_open]) + "\n"
        values += str(("None","Do not disturb")[self.ss.do_not_disturb]) + "\n"
        values += str(("No","Yes")[self.ss.noisy_outside]) + "\n"
        values += str(("No","Yes")[self.ss.busy_in_15_minutes]) + "\n"
        values += str(("No","Yes")[self.ss.favorable_conditions])
        
        # draw_rotated_text(self.display.buffer, 'smoke value: ', (150, 200), 90, text, fill=(0,0,0))
        # draw_rotated_text(self.display.buffer, "{:.4f} ppm".format(self.ss.smoke / 1000), (170, 230), 90, text, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, "ClassMate", (24, 22), 0, titleFont, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, "Classroom State", (200, 100), 270, subTitleFont, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, index, (10, 100), 270, text, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, values, (10, 250), 270, text, fill=(0,0,0))
        # draw_rotated_text(self.display.buffer, f"{self.ss.co2} ppm", (170, 10), 90, font, fill=(0,0,0))
        self.display.display()

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

if __name__ == "__main__":    
    speaker = Speaker(50, "Resources/Audio/Testing/demo_audio.mp3")
    speaker.playForTime(5)
    client = Client("ws://localhost:8888/websocket", 5)