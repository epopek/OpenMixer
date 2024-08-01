from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from tkinter import *
from tkinter import ttk
import serial
import serial.tools.list_ports
import ast
import threading
import time

class OpenMixer:
    def __init__(self):
        super().__init__()
        
        self.window = Tk()  # Initialize window
        self.window.geometry("1000x500")  # Set window size in pixels
        self.window.title("OpenMixer")

        self.all_apps = ['Firefox']
        
        self.sessions = AudioUtilities.GetAllSessions()
        
        # Initialize threading event for thread stopping
        self.stop_event = threading.Event()

        self.detectedPotsAndFunctions = []
        self.active_ports = []
        
        # Find available ports
        self.find_available_ports()
        
        self.SelectPortsBox = ttk.Combobox(state='readonly', values=self.active_ports, width=50) 
        self.SelectPortsBox.set('Select Port')
        self.SelectPortsBox.bind("<<ComboboxSelected>>", self.EstablishPortConnection)

        self.SelectPortsBox.grid(row=5, column=5)    

        self.CreatePotComboFunctionBoxes()

        # Set up the shutdown protocol
        self.window.protocol("WM_DELETE_WINDOW", self.Shutdown)
        self.window.mainloop()
        
    def changeVolume(self, app, volume_level):
        try:
            for session in self.sessions: 
                process = session.Process
                if process and app.lower() in process.name().lower(): 
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(volume_level, None)
                    print(f"Set volume for {app} to {volume_level * 100}%")
        except Exception as e:
            print(f"Error changing volume: {e}")

    def Return_COM_Index(self): 
        return self.SelectPortsBox.current()
    
    def find_available_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.active_ports.append(f"['{port.device}', '{port.description}', '{port.manufacturer}']")
                  
    def EstablishPortConnection(self, event):
        selected = self.Return_COM_Index()
        selected = self.active_ports[selected]
        selected = ast.literal_eval(selected)

        self.selected_port = serial.Serial(f"{selected[0]}", 9600)
        
        self.stop_event.clear()  # Reset the stop event
        self.thread = threading.Thread(target=self.ReadAndProcess)
        self.thread.start()

    def ReadAndProcess(self):
        num = 0
        while not self.stop_event.is_set():
            try:
                if not self.selected_port.is_open:
                    print("Serial port is closed. Exiting.")
                    break
                
                read_data = self.selected_port.readline().decode("utf-8").strip()
                data_to_list = [x.strip() for x in read_data.split(",") if x.strip()]

                if not data_to_list:
                    print("No data received")
                    continue

                if num >= len(self.detectedPotsAndFunctions):
                    num = 0

                pot_function = self.detectedPotsAndFunctions[num]
                pot_index = pot_function[1]
                app_name = pot_function[2]

                if pot_index < len(data_to_list):
                    try:
                        volume_value = int(data_to_list[pot_index]) / 100
                        self.changeVolume(app_name, volume_value)
                    except ValueError:
                        print(f"Error: Invalid volume value received: {data_to_list[pot_index]}")
                else:
                    print(f"Error: Index {pot_index} not in range")
                num += 1

            except IndexError:
                print(f"Error reading and processing data")
                continue

            except Exception as e:
                print(f"Unexpected Error - {e}")
                self.stop_event.set()
    
            time.sleep(0.1)  # Sleep to avoid high CPU usage

        self.close_port()

    def close_port(self):
        if self.selected_port and self.selected_port.is_open:
            print("Closing serial port...")
            self.selected_port.close()
            print("Serial port closed.")

    def Shutdown(self):
        # Signal the thread to stop
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)  # Wait for the thread to finish
            if self.thread.is_alive():
                print("Thread did not exit in time. Forcefully exiting.")
        
        # Close the port
        self.close_port()
        
        # Close the Tkinter window
        self.window.destroy()

    def SetPotFunctions(self, id, pot_num, pot_name):
        selected_func = id.widget.get()
        self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func])

    def CreatePotComboFunctionBoxes(self):
        boxes = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"]
        grid_space = 0
        
        for index, name in enumerate(boxes):
            potbox = ttk.Combobox(self.window, values=self.all_apps)
            potbox.grid(row=1 + grid_space, column=2)
            potbox.bind("<<ComboboxSelected>>", lambda id, idx=index, n=name: self.SetPotFunctions(id, idx, n))
            
            potlabel = Label(self.window, text=name)
            potlabel.grid(row=1 + grid_space, column=4)
            grid_space += 4

    def DetectNewPrograms(self): 
        while not self.stop_event.is_set():
            self.sessions = AudioUtilities.GetAllSessions()
            time.sleep(2)

    def IterateNewPrograms(self):
        try:
            for session in self.sessions:
                process = session.Process
                if process:
                    process_name = process.name()
                    if process_name not in self.all_apps:
                        self.all_apps.append(process_name)
                        print(process_name)
        except Exception as e:
            print(f"Error iterating new programs: {e}")

    def IsWindowClosed(self):
        return not self.window.winfo_exists()

if __name__ == "__main__":
    OpenMixer()