import tkinter as tk
from tkinter import filedialog, ttk
import serial
from PIL import Image
import time
import threading


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.master.title("Serial Gif Sender")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.select_file = ttk.Button(self, text="Select file", command=self.load_file)
        self.select_file.pack(pady=20)

        self.start = ttk.Button(self, text="Start", command=self.start_process)
        self.start.pack(pady=10)

        self.stop = ttk.Button(self, text="Stop", command=self.stop_process)
        self.stop.pack(pady=10)
        self.stop["state"] = "disabled"

        self.running = False

    def load_file(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("gif files", "*.gif"), ("all files", "*.*")))

    def start_process(self):
        self.start["state"] = "disabled"
        self.stop["state"] = "normal"
        self.running = True
        threading.Thread(target=self.run_process).start()

    def stop_process(self):
        self.running = False
        self.stop["state"] = "disabled"
        self.start["state"] = "normal"

    def run_process(self):
        ser = serial.Serial(
            port='COM7',
            baudrate=57600,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        frame = Image.open(self.filename)
        nframes = 0

        hexar = []

        startbit = [0x80, 0x83, 0x01]
        endbit = 0x8F

        while self.running:
            frame.seek(nframes)
            pix = frame.convert("1").load()

            hexar = []

            for x in range(0, 28):
                row = ""
                for y in range(0, 7):
                    thispix = int(pix[x, y])
                    if thispix > 0:
                        thispix = 1
                    row = str(thispix) + row

                hexar.append(int(row, 2))

            for x in startbit:
                ser.write(bytes([x]))
            for y in hexar:
                ser.write(bytes([y]))

            ser.write(bytes([endbit]))

            nframes += 1

            if nframes >= frame.n_frames:
                nframes = 0

            time.sleep(.55)


root = tk.Tk()
app = Application(master=root)
app.mainloop()
