import time
import serial
from PIL import Image, ImageDraw, ImageFont
from tkinter import Tk, Label, Entry, Button, StringVar, Grid

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

def send_to_flipdot(pixels):
    for x in startbit: 
        ser.write(bytes([x]))
    for y in pixels:
        ser.write(bytes([y]))
    ser.write(bytes([endbit]))

def send_text():
    text = text_var.get()
    font = ImageFont.truetype("calibri.ttf", 8)  
    text_image = Image.new('1', (28, 7))  
    draw = ImageDraw.Draw(text_image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    start_x = (text_image.width - text_width) // 3
    start_y = (text_image.height - text_height) // 6
    draw.text((start_x, start_y), text, font=font, fill=255)
    pix = text_image.load()
    hexar = [int(''.join(str(int(pix[27-x, y] > 0)) for y in range(7)), 2) for x in range(28)]
    send_to_flipdot(hexar)


def all_white():
    send_to_flipdot([0x7F] * 28)

def all_black():
    send_to_flipdot([0x00] * 28)

def checkerboard():
    send_to_flipdot([0x55, 0xAA] * 14)

root = Tk()

Label(root, text="Enter text:").grid(row=0, column=0, sticky="w")

text_var = StringVar()
Entry(root, textvariable=text_var).grid(row=1, column=0, sticky="ew")

Button(root, text="Send Text", command=send_text).grid(row=2, column=0, sticky="ew")

Button(root, text="All White", command=all_white).grid(row=3, column=0, sticky="ew")
Button(root, text="All Black", command=all_black).grid(row=4, column=0, sticky="ew")
Button(root, text="Checkerboard", command=checkerboard).grid(row=5, column=0, sticky="ew")

# Configure the grid to expand
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=1)

root.mainloop()
