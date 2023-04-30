import time
import serial
from PIL import Image, ImageDraw, ImageFont

ser = serial.Serial(
    port='COM7',
    baudrate=57600,
    timeout=1,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Set index and start commands for matrix
startbit = [0x80, 0x83, 0x01]

# Set endbit for matrix
endbit = 0x8F

# Get text input from the user
text = input("Enter the text to display: ")

# Create an image of the text
font = ImageFont.truetype("calibri.ttf", 7)  # Specify a font and size that fits your display
text_image = Image.new('1', (28, 7))  # Create a new black image
draw = ImageDraw.Draw(text_image)

# Get the bounding box of the text
bbox = draw.textbbox((0, 0), text, font=font)

# Calculate the width and height of the text
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Calculate the starting position of the text
start_x = (text_image.width - text_width) // 3
start_y = (text_image.height - text_height) // 6

# Draw the text onto the image
draw.text((start_x, start_y), text, font=font, fill=255)

while True:
    # Load text image pixels
    pix = text_image.load()
    
    # Init the list for holding matrix chars
    hexar = []

    # Loop through 28 pixels width
    for x in range(0, 28):
        row = ""
        # Loop seven pixels down, add to binary string
        for y in range(0, 7):
            thispix = int(pix[x, y])
            if (thispix > 0): thispix = 1
            row = str(thispix) + row
        # Convert binary string to integer and add to output list
        hexar.append(int(row, 2))

    # Write to matrix
    for x in startbit: 
        ser.write(bytes([x]))
    for y in hexar:
        ser.write(bytes([y]))

    ser.write(bytes([endbit]))

    # Wait to give matrix time to update
    time.sleep(.55)
