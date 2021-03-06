# sockets and threading
from multiprocessing.pool import ThreadPool
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import time

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
import Adafruit_GPIO.SPI as SPI

# sound sensor
import RPi.GPIO as GPIO


THIS_CLIENT_ID = CLIENT_ID_LOGIC

#display
DC = 5
RST = 6
SPI_PORT = 0
SPI_DEVICE = 0

# sound sensor
SOUND_PIN = 16

# flip switch
SWITCH_PIN = 20

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
        run_background(play_audio, self.on_complete, (100, "Resources/Audio/mac_startup.mp3", 5))
        
        self.ss = SystemState()
        
        print ("Setting up TFT screen...")
        self.display = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
        self.display.begin()
        self.inititalize_screen()
        
        systemDatabase.truncate()
        systemDatabase.drop_tables()
        # systemDatabase.insert({"temperature_outside": 0})
        # systemDatabase.insert({"humidity_outside": 0})
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.recentSoundMeasurement = time.time()
        
        # sound sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SOUND_PIN, GPIO.IN)
        GPIO.add_event_detect(SOUND_PIN, GPIO.BOTH, bouncetime=300)
        GPIO.add_event_callback(SOUND_PIN, self.soundDetect)
        
        # switch
        GPIO.setup(SWITCH_PIN, GPIO.IN)
        
        
        
        print ("Setting up Gas Detection...")
        self.gas_detection = GasDetection()
        
        print ("Connecting to WebSocket Server...")
        self.connect()
        PeriodicCallback(self.keep_alive, 10000, io_loop=self.ioloop).start()
        PeriodicCallback(self.status_update, 10000, io_loop=self.ioloop).start()
        
        run_background(play_audio, self.on_complete, (80, "Resources/Audio/welkom_bij_classmate.mp3", 5))
        
        # self.status_update()
        
        self.ioloop.start()
        


    @gen.coroutine
    def connect(self):
        print("Connecting...")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            print("Connection error")
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
            
            elif (msg.action == ACTION_OPEN_DOOR): # If the door was opened after it's been requested to do so:
                self.ss.door_open = True
                self.status_screen()
                
            elif (msg.action == ACTION_CLOSE_DOOR): # If the door was closed after it's been requested to do so:
                self.ss.door_open = False
                self.status_screen()
                
            elif (msg.action == ACTION_SET_BUSY_IN_15_MINUTES): # If the door was closed after it's been requested to do so:
                self.ss.busy_in_15_minutes = True
                self.status_screen()
                
            elif (msg.action == ACTION_SET_NOT_BUSY_IN_15_MINUTES): # If the door was closed after it's been requested to do so:
                self.ss.busy_in_15_minutes = False
                self.status_screen()
                
            elif (msg.action == ACTION_ACTIVATE_DO_NOT_DISTURB):
                self.ss.do_not_disturb = True
                run_background(play_audio, self.on_complete, (50, "Resources/Audio/do_not_disturb_activated.mp3", 5))
                
            elif (msg.action == ACTION_DEACTIVATE_DO_NOT_DISTURB):
                self.ss.do_not_disturb = False
                run_background(play_audio, self.on_complete, (50, "Resources/Audio/do_not_disturb_deactivated.mp3", 5))
                
            elif (msg.action == ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE):
                self.ss.temperature_outside = float(msg.data["temperature"]) - 2 # with correction
                self.ss.humidity_outside = float(msg.data["humidity"]) - 10 # with correction
                
            elif (msg.action == ACTION_RICKROLL):
                run_background(play_audio, self.on_complete, (100, "Resources/Audio/demo_audio.mp3", 5))

    def on_complete(self, res):
        _workers
        # print("Test {0}".format(res))
        
    def soundDetect(self, channel):
        # print ("SOUND DETECTED", time.time() - self.recentSoundMeasurement)
        self.recentSoundMeasurement = time.time()

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            msg = "Keeping connection alive."
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_ALIVE, {"user": CLIENT_ID_LOGIC, "message": msg}).toJSON())
            
    def status_update(self):
        do_not_disturb_switch = (GPIO.input(SWITCH_PIN) == 1)
        if (self.ss.do_not_disturb != None) and (self.ss.do_not_disturb != do_not_disturb_switch):
            run_background(play_audio, self.on_complete, (100, "Resources/Audio/do_not_disturb_activated.mp3" if do_not_disturb_switch else "Resources/Audio/do_not_disturb_deactivated.mp3", 5))
        self.ss.do_not_disturb = do_not_disturb_switch # if the pin is high, set to True

        if (time.time() - self.recentSoundMeasurement <= 5):
            self.ss.noisy_outside = True
        else:
            self.ss.noisy_outside = False
            
        temperature_inside = readTemperatureInside()
        if (temperature_inside):
            self.ss.temperature_inside = temperature_inside
            
        humidity_inside = readHumidityInside()
        if (humidity_inside):
            self.ss.humidity_inside = humidity_inside
            
        co2 = mh_z19.read_co2valueonly()
        if (co2):
            self.ss.co2 = co2
            
        ppm = self.gas_detection.percentage()
        if (ppm):
            self.ss.co = ppm[self.gas_detection.CO_GAS] * 1000
            self.ss.smoke = ppm[self.gas_detection.SMOKE_GAS] * 1000
        
        danger = None
        open_door_points = 0
            
        self.ss.points_co2 = ((self.ss.co2 - 800) / 100)
            
        self.ss.points_temperature = self.ss.temperature_inside - self.ss.temperature_outside
            
        self.ss.points_humidity = ((self.ss.humidity_inside - self.ss.humidity_outside) / 10)
        
        open_door_points = self.ss.points_co2 + self.ss.points_temperature + self.ss.points_humidity
        
        if (open_door_points <= 2):
            self.ss.favorable_conditions = True
        
        if self.ss.noisy_outside and self.ss.do_not_disturb:
            # if it's noisy and do not disturb is activated
            #   we should fake that the conditions are favorable
            #   so the door will be closed
            open_door_points -= 5
            
        print ("'Open door points':", open_door_points)
        
        # danger in increasing order:
        #   False, None, True
        
        if self.ss.smoke > 40:
            danger = True
            # if not self.ss.do_not_disturb:
            run_background(play_audio, self.on_complete, (50, "Resources/Audio/alarm.mp3", 5))
        elif self.ss.co2 > 1500:
            danger = True
            if not self.ss.do_not_disturb or self.ss.co2 > 1800:
                run_background(play_audio, self.on_complete, (80, "Resources/Audio/co2_gevaarlijk_hoog.mp3", 5))
        elif self.ss.co2 > 1300:
            danger = True
            # if not self.ss.do_not_disturb: run_background(play_audio, self.on_complete, (80, "Resources/Audio/co2_te_hoog.mp3", 5))
        elif self.ss.co2 > 1100:
            danger = True
            # if not self.ss.do_not_disturb: run_background(play_audio, self.on_complete, (80, "Resources/Audio/co2_hoog.mp3", 5))
        elif open_door_points <= 3:
            danger = False
        else:
            danger = None

        print (danger)
        
        if (danger or open_door_points > 2 or ((open_door_points > 0) and (self.ss.busy_in_15_minutes == True))) and (self.ss.door_open == False or self.ss.door_open == None):
            print ("Opening door...")
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_OPEN_DOOR, "").toJSON())
        elif (not danger) and (open_door_points <= 2) and (self.ss.door_open == True):
            print ("Closing door...")
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_CLOSE_DOOR, "").toJSON())
        
        if (danger == False):
            self.status_screen((50,205,50))
        elif (danger == True):
            self.status_screen((205,50,50))
        else:
            self.status_screen((50,100,50))
            
        
        self.ss.favorable_conditions = False if (danger != False) else True
            
        ssDict = vars(self.ss)
        dbDict = {
            "t_i": self.ss.temperature_inside,
            "t_o": self.ss.temperature_outside,
            "h_i": self.ss.humidity_inside,
            "h_o": self.ss.humidity_outside,
            "co2": self.ss.co2,
            "co": self.ss.co,
            "s": self.ss.smoke,
            "n_o": self.ss.noisy_outside,
            "d_o": self.ss.door_open,
            "d_n_d": self.ss.do_not_disturb,
            "f_c": self.ss.favorable_conditions
        }
        
        systemDatabase.insert(dbDict)
        # the data above should also be written to a database, for easy history / algoritmic usage and plotting.
        # should include time
        historic_data = systemDatabase.all()
        historic_data = historic_data[-50:]
        try:
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_STATUS_UPDATE, ssDict).toJSON())
            self.ws.write_message(Message(THIS_CLIENT_ID, ACTION_STATUS_HISTORY, historic_data).toJSON())
        except Exception as e:
            print ("Sending status update went wrong.")
            
    def inititalize_screen(self):
        self.display.clear((255,255,255))

        draw = self.display.draw()

        # Draw a green rectangle with black outline.
        draw.rectangle((0, 320, 240, 90), outline=(0,0,0), fill=(50,205,50))

        # Load default font.
        titleFont = ImageFont.truetype("arial.ttf", 40)
        subTitleFont = ImageFont.truetype("arial.ttf", 16)
        
        draw_rotated_text(self.display.buffer, "ClassMate", (24, 22), 0, titleFont, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, "Starting up...", (200, 100), 270, subTitleFont, fill=(0,0,0))

        self.display.display()
            
    def status_screen(self, fill_parameter = (50,205,50)):
        self.display.clear((255,255,255))

        draw = self.display.draw()

        # Draw a green rectangle with black outline.
        draw.rectangle((0, 320, 240, 90), outline=(0,0,0), fill=fill_parameter)

        # Load default font.
        titleFont = ImageFont.truetype("arial.ttf", 40)
        subTitleFont = ImageFont.truetype("arial.ttf", 16)
        text = ImageFont.truetype("arial.ttf", 12)
        
        index = values = ""
        
        index = "Temperature Inside\n"
        index += "Temperature Outside\n"
        index += "Humidity Inside\n"
        index += "Humidity Outside\n"
        index += "CO2 Concentration\n"
        index += "CO Concentration\n"
        index += "Smoke Concentration\n"
        index += "Door\n"
        index += "Do not disturb active?\n"
        index += "Noisy outside?\n"
        index += "Class used in 15 min?\n"
        index += "Favorable conditions?"
        
        for _ in range(max(0,int(self.ss.points_temperature))): values += "!"
        values += str(self.ss.temperature_inside) + "??C\n"
        values += str(self.ss.temperature_outside) + "??C\n"
        
        for _ in range(max(0,int(self.ss.points_humidity))): values += "!"
        values += str(self.ss.humidity_inside) + "%\n"
        values += str(self.ss.humidity_outside) + "%\n"
        
        for _ in range(max(0,int(self.ss.points_co2))): values += "!"
        values += str(self.ss.co2) + " ppm\n"
        
        values += str("{:.4f} ppm".format(self.ss.co / 1000)) + "\n"
        
        for _ in range(max(0,int((self.ss.smoke - 40) / 10))): values += "!"
        values += str("{:.4f} ppm".format(self.ss.smoke / 1000)) + "\n"
        
        if (self.ss.door_open == None):
            values += "Unknown\n"
        else:
            values += str(("Closed","Open")[self.ss.door_open]) + "\n"
        values += str(("No","Yes")[self.ss.do_not_disturb]) + "\n"
        values += str(("No","Yes")[self.ss.noisy_outside]) + "\n"
        values += str(("No","Yes")[self.ss.busy_in_15_minutes]) + "\n"
        values += str(("No","Yes")[self.ss.favorable_conditions])
        
        draw_rotated_text(self.display.buffer, "ClassMate", (24, 22), 0, titleFont, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, "Classroom State", (200, 100), 270, subTitleFont, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, index, (10, 100), 270, text, fill=(0,0,0))
        draw_rotated_text(self.display.buffer, values, (10, 250), 270, text, fill=(0,0,0))
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
    # print ("a")
    # speaker = Speaker(50, "Resources/Audio/demo_audio.mp3")
    # speaker.playForTime(5)
    # print ("b")
    # print ("c")
    # a = Speaker(50, "Resources/Audio/demo_audio.mp3")
    # a.playForTime(5)
    # print ("d")
    client = Client("ws://localhost:8888/websocket", 5)
