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
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.master.title("Flip Dot GIF Sender")
        self.master.geometry("500x300")  # Increased window size
        self.master.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Custom colors and styling
        self.style.configure('TFrame', background='light steel blue')
        self.style.configure('TButton',
                             foreground='black',
                             background='deep sky blue',
                             font=('Helvetica', 12, 'bold'),
                             borderwidth=1)
        self.style.map('TButton',
                       foreground=[('pressed', 'red'), ('active', 'blue')],
                       background=[('pressed', '!disabled', 'black'), ('active', 'white')],
                       highlightcolor=[('focus', 'green'), ('!focus', 'red')],
                       relief=[('pressed', 'groove'), ('!pressed', 'ridge')])

        self.select_file = ttk.Button(self, text="Select file", command=self.load_file)
        self.select_file.place(relx=0.5, rely=0.3, anchor='center')  # Centered buttons

        self.start = ttk.Button(self, text="Start", command=self.start_process)
        self.start.place(relx=0.5, rely=0.5, anchor='center')

        self.stop = ttk.Button(self, text="Stop", command=self.stop_process)
        self.stop.place(relx=0.5, rely=0.7, anchor='center')
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