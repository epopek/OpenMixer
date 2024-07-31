from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
from ctypes import cast, POINTER
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter 
import serial
import serial.tools.list_ports
import ast
import threading
import configparser
import time

class OpenMixer:

    def __init__(self):
        super().__init__()
        
        self.window = Tk() #initialize window
        self.window.geometry("1000x500")#set window size in pixels
        self.window.title("OpenMixer")

        self.all_apps = ['Firefox']
        
        self.sessions = AudioUtilities.GetAllSessions()

        self.ProgramDetectionThread = threading.Thread(target=self.DetectNewPrograms)
        self.ProgramDetectionThread.start()
        #self.IterateNewPrograms()

        self.detectedPotsAndFunctions = []
        self.active_ports = []

        def findAvailiblePorts():
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.active_ports.append(f"['{port.device}', '{port.description}', '{port.manufacturer}']")
                  
        findAvailiblePorts()
        
        self.SelectPortsBox = ttk.Combobox(state='readonly', values=self.active_ports, width=50) 
        self.SelectPortsBox.set('Select Port')
        self.SelectPortsBox.bind("<<ComboboxSelected>>", self.EstablishPortConnection)

        self.SelectPortsBox.grid(row=5, column=5)    

        self.CreatePotComboFunctionBoxes()

        self.window.protocol("WM_DELETE_WINDOW", self.Shutdown)
        self.window.mainloop()
        
    def changeVolume(self, app, volume_level):
            try: #need this try and except block otherwise the tkinter window would crash
                for session in self.sessions: 
                    process = session.Process# Get the process associated with the session
                    if process and app.lower() in process.name().lower(): 
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        volume.SetMasterVolume(volume_level, None)# Set the volume level
                        print(f"Set volume for {app} to {volume_level * 100}%")
            except:
                pass
    def Return_COM_Index(self): 
            index_COM = self.SelectPortsBox.current()
            return index_COM
    
    def EstablishPortConnection(self, event):
            selected = self.Return_COM_Index()
            selected = self.active_ports[selected]
            selected = ast.literal_eval(selected)

            self.selected_port = serial.Serial(f"{selected[0]}", 9600)
            
            self.thread = threading.Thread(target=self.ReadAndProcess) #Run the ReadAndProcess function similtaneously otherwise the tkinter window is unable to update and crashes
            self.thread.start()

    def ReadAndProcess(self):
        num = 0
        while True:
            try:
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

            except Exception as e:
                if self.window.winfo_exists():############################################################## TODO - this needs to check if the window is open and if its not the function needs to shutdown
                    print("The window is open.")
                else:
                    print("The window is closed.")
                print(f"Error reading and processing data: {e}")
                #messagebox.showerror("Please select a program to control")

            finally:
                if not self.selected_port.is_open: #close the serial port when the GUI is closed (otherwise it gets stuck in an infinite error loop)
                    break
    
    def Shutdown(self):
        try: #otherwise the user cannot close the window until a COM port is selected
            self.window.destroy()  # Close the Tkinter window
            self.selected_port.close()
        except AttributeError:
            #self.window.destroy()
            pass

    def SetPotFunctions(self, id, pot_num, pot_name):
        #print(pot_num, pot_name)
        selected_func = id.widget.get()
        #print(selected_func)
        self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func])

    def CreatePotComboFunctionBoxes(self):
        boxes = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"]
        grid_space = 0
        
        for index, name in enumerate(boxes):
            potbox = ttk.Combobox(self.window, values=self.all_apps)
            potbox.grid(row=1+grid_space, column=2)
            potbox.bind("<<ComboboxSelected>>", lambda id, idx=index, n=name: self.SetPotFunctions(id, idx, n))
            
            potlabel = Label(self.window, text=name)
            potlabel.grid(row=1+grid_space, column=4)
            grid_space += 4

    def StartUp():
        query_numberofPOTS = self.selected_port.send("?POTS\n")
        return query_numberofPOTS
    
    def DetectNewPrograms(self): #Constantly searches for new programs that were opened and can be controlled
        while True:
            self.sessions = AudioUtilities.GetAllSessions()
            time.sleep(2)
    
    def IterateNewPrograms(self):####################################################################################TODO - this needs to iterate through all active programs and add them to the comboboxes
        try: #need this try and except block otherwise the tkinter window would crash
           
           for session in sessions:
                process = session.Process
                print(process)
                if process:
                    process_name = process.name()
                    self.all_apps.append(process_name)
                    print(process.name())
        except:
            pass
    
    def IsWindowClosed(self):
        return self.window.winfo_exists()
OpenMixer()