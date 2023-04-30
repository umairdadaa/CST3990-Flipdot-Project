import time
import serial
from PIL import Image

ser = serial.Serial(
    port='COM7',
    baudrate=57600,
    timeout=1,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

frame = Image.open("timer.gif")
nframes = 0

hexar = []

# Set index and start commands for matrix
startbit = [0x80, 0x83, 0x01]

# Set endbit for matrix
endbit = 0x8F

while True:
    # Load frame pixels
    frame.seek(nframes)
    pix = frame.convert("1").load()
    
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

    # Step up frame counter
    nframes += 1

    # Check for more frames in GIF
    if nframes >= frame.n_frames:
        # GIF is EOF (last frame done), start over
        nframes = 0

    # Wait to give matrix time to update
    time.sleep(.55)
