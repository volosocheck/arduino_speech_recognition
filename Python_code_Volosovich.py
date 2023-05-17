from vosk import Model, KaldiRecognizer
import tkinter as tk
from pyfirmata import Arduino
from time import sleep
import serial
import pyaudio
from threading import Thread

model = Model(r"C:\Users\volos\Desktop\speech_python_arduino\vosk-model-small-ru-0.22") # полный путь к модели
rec = KaldiRecognizer(model, 16000)
ArduinoSerial = serial.Serial("COM3" ,9600)

class LampWidget(tk.Frame):
    def __init__(self, master=None, label='', **kwargs):
        super().__init__(master, **kwargs)
        self.label = label
        self.color = 'red'
        self.canvas = tk.Canvas(self, width=10, height=10, bg='white', highlightthickness=0)
        self.canvas.create_oval(1, 1, 9, 9, fill=self.color, outline='black', width=0.1)
        self.label_widget = tk.Label(self, text=label)
        self.canvas.pack(side='right', padx=5)
        self.label_widget.pack(side='left')

    def set_on(self, on=True):
        self.color = '#00cc00' if on else '#ff3333'
        self.canvas.itemconfigure(1, fill=self.color)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Умный дом Волосовича Ильи ИБ-81з")
        self.pack()
        self.create_widgets()
        self.recording = False
        self.thread = None

    def create_widgets(self):
        self.start_button = tk.Button(self, text="Начать запись", font=("Arial", 16), command=self.start_recording)
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = tk.Button(self, text="Остановить запись", font=("Arial", 16), command=self.stop_recording, state="disabled")
        self.stop_button.pack(side="right", padx=10, pady=10)

        self.result_text = tk.Text(self, width=40, height=10, font=("Arial", 14))
        self.result_text.pack()

        self.blue_lamp = LampWidget(label='Голубая лампочка')
        self.blue_lamp.pack(side='top', anchor='w', padx=10, pady=1)
        self.red_lamp = LampWidget(label='Красная лампочка')
        self.red_lamp.pack(side='top', anchor='w', padx=10, pady=1)
        self.green_lamp = LampWidget(label='Зеленая лампочка')
        self.green_lamp.pack(side='top', anchor='w', padx=10, pady=1)
        self.fan = LampWidget(label='Вентилятор             ')
        self.fan.pack(side='top', anchor='w', padx=10, pady=1)
        self.light = LampWidget(label='Свет                          ')
        self.light.pack(side='top', anchor='w', padx=10, pady=1)

    def start_recording(self):
        self.recording = True
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        self.thread = Thread(target=self.record)
        self.thread.start()

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )

        while self.recording:
            data = stream.read(4000)
            if rec.AcceptWaveform(data):
                command = rec.Result()
                command = command[command.index(':')+3:-3]
                self.result_text.insert(tk.END, command + "\n")
                self.result_text.see(tk.END)
                if 'включи голуб' in command:
                    ArduinoSerial.write(str.encode('B'))
                    self.blue_lamp.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда включить голубую лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'включи кра' in command:
                    ArduinoSerial.write(str.encode('R'))
                    self.red_lamp.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда включить красную лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'включи зел' in command:
                    ArduinoSerial.write(str.encode('G'))
                    self.green_lamp.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда включить зеленую лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи голуб' in command:
                    ArduinoSerial.write(str.encode('Z'))
                    self.blue_lamp.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить голубую лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи кра' in command:
                    ArduinoSerial.write(str.encode('X'))
                    self.red_lamp.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить красную лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи зел' in command:
                    ArduinoSerial.write(str.encode('C'))
                    self.green_lamp.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить зеленую лампочку\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'включи все' in command:
                    ArduinoSerial.write(str.encode('V'))
                    self.blue_lamp.set_on(True)
                    self.red_lamp.set_on(True)
                    self.green_lamp.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда включить все лампочки\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи все' in command:
                    ArduinoSerial.write(str.encode('M'))
                    self.blue_lamp.set_on(False)
                    self.red_lamp.set_on(False)
                    self.green_lamp.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить все лампочки\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'гирлянд' in command:
                    self.result_text.insert(tk.END, "Отправлена команда включить гирлянду\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                    for _ in range(15):
                        ArduinoSerial.write(str.encode('B'))
                        self.blue_lamp.set_on(True)
                        sleep(0.05)
                        ArduinoSerial.write(str.encode('Z'))
                        self.blue_lamp.set_on(False)
                        sleep(0.05)
                        ArduinoSerial.write(str.encode('R'))
                        self.red_lamp.set_on(True)
                        sleep(0.05)
                        ArduinoSerial.write(str.encode('X'))
                        self.red_lamp.set_on(False)
                        sleep(0.05)
                        ArduinoSerial.write(str.encode('G'))
                        self.green_lamp.set_on(True)
                        sleep(0.05)
                        ArduinoSerial.write(str.encode('C'))
                        self.green_lamp.set_on(False)
                        sleep(0.05)
                elif 'покажи список команд' in command:
                    self.result_text.insert(tk.END, "Список всех команд:\n1. включи красную\n2. выключи красную\n3. включи голубую\n4. выключи голубую\n5. включи зеленую\n6. выключи зеленую\n7. гирлянда\n8. включи свет\n9. выключи свет\n10. включи вентилятор\n11. выключи вентилятор", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'сохрани список команд' in command:
                    with open("commands.txt", "w", encoding="utf-8") as f:
                        f.write('Список всех команд:\n1. включи красную\n2. выключи красную\n3. включи голубую\n4. выключи голубую\n5. включи зеленую\n6. выключи зеленую\n7. гирлянда\n8. включи свет\n9. выключи свет\n10. включи вентилятор\n11. выключи вентилятор')
                    self.result_text.insert(tk.END, "Список команд сохранен в файле commands.txt\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'включи вентил' in command:
                    ArduinoSerial.write(str.encode('P'))
                    self.fan.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда выключить вентилятор\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи вентил' in command:
                    ArduinoSerial.write(str.encode('O'))
                    self.fan.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить вентилятор\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'включи свет' in command:
                    ArduinoSerial.write(str.encode('H'))
                    self.light.set_on(True)
                    self.result_text.insert(tk.END, "Отправлена команда включить свет\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)
                elif 'выключи свет' in command:
                    ArduinoSerial.write(str.encode('L'))
                    self.light.set_on(False)
                    self.result_text.insert(tk.END, "Отправлена команда выключить свет\n", "success")
                    self.result_text.tag_config("success", foreground="green")
                    self.result_text.see(tk.END)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop_recording(self):
        self.recording = False
        self.thread.join()
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"

root = tk.Tk()
app = Application(master=root)
app.mainloop()