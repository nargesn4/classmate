from time import sleep
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from gas_detection import GasDetection
import mh_z19
# numpy

# Raspberry Pi configuration.
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# result = mh_z19.read_co2valueonly()
# print (result)

# smoke_detector = GasDetection()
# ppm = smoke_detector.percentage()
# smoke_value = ppm[smoke_detector.SMOKE_GAS]
# print (smoke_value)
# smoke_value_string = str(round(smoke_value, 2))
# smoke_value_string = "ok"

smoke_value_string = str(mh_z19.read_co2valueonly())
print (smoke_value_string)


# Initialize display. BCM2711

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

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
disp.begin()
while True:

    disp.clear((255,255,255))

    draw = disp.draw()

    # Draw a purple rectangle with yellow outline.
    draw.rectangle((10, 155, 110, 10), outline=(255,255,0), fill=(50,205,50))

    # Draw a green rectangle with black outline.
    draw.rectangle((10, 310, 110, 165), outline=(0,0,0), fill=(50,205,50))

    # Load default font.
    font = ImageFont.load_default()
    
    draw_rotated_text(disp.buffer, 'CO2 value!', (150, 40), 90, font, fill=(0,0,0))
    draw_rotated_text(disp.buffer, 'This is a line of text.', (170, 10), 90, font, fill=(0,0,0))
    draw_rotated_text(disp.buffer, 'smoke value: ', (150, 200), 90, font, fill=(0,0,0))
    draw_rotated_text(disp.buffer, smoke_value_string , (170, 230), 90, font, fill=(0,0,0))
    disp.display()
    smoke_value_string += "a"
    sleep(2)
