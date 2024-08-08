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
import configparser
import os 

class OpenMixer:

    def __init__(self):
        super().__init__()
        
        self.window = Tk() #initialize window
        self.window.geometry("1000x500")#set window size in pixels
        self.window.title("OpenMixer")

        self.stop_event = threading.Event() #This is the stop event for all the threads and helps them shut down when the program is closed
        
        self.all_apps = [] 
        self.potboxlist = []
        
        self.sessions = AudioUtilities.GetAllSessions()
        self.devices = AudioUtilities.GetAllDevices()

        self.ProgramDetectionThread = threading.Thread(target=self.DetectNewPrograms)
        self.ProgramDetectionThread.start()
        #self.IterateNewPrograms()

        self.detectedPotsAndFunctions = []
        self.active_ports = []
        
        self.config = configparser.ConfigParser()
        self.SetupFile = "OpenMixerSetup.ini"
        self.ReadConfigFile()
        if os.path.exists(self.SetupFile) == False:
            with open(self.SetupFile, "x") as f:
                print('Created') 

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
            try:
                selected = self.Return_COM_Index()
                selected = self.active_ports[selected]
                selected = ast.literal_eval(selected)

                self.selected_port = serial.Serial(f"{selected[0]}", 9600)
                
                self.stop_event.clear()
                self.thread = threading.Thread(target=self.ReadAndProcess) #Run the ReadAndProcess function similtaneously otherwise the tkinter window is unable to update and crashes
                self.thread.start()
            except Exception as e:
                messagebox.showerror("Port Busy",message=f"Port: {selected[0]} is currently in use by another application")

    def ReadAndProcess(self):
        num = 0
        while not self.stop_event.is_set():
            try:
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
                            if app_name != 'microphone':
                                self.changeVolume(app_name, volume_value)
                            elif app_name =='microphone':
                                self.set_microphone_volume(volume_value)
                        except ValueError:
                            print(f"Error: Invalid value received: {data_to_list[pot_index]}")
                    else:
                        print(f"Error: Index {pot_index} not in range")
                    num += 1

                except IndexError:
                    print(f"Error reading and processing data")
                    continue #IndexError is called if the user connects to the Active COM port before selecting a program to control with the pots.
               
            except AttributeError:
                print('here')
           
            except Exception as e:
                print(f"Unexpected Error - {e}")
                self.stop_event.set()

    def Shutdown(self):
        self.stop_event.set()
        self.window.destroy() #destroy the window before closing the threads to make it appear that the program has been closed 
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2) #wait 2 seconds to close the active threads otherwise weird errors occur
        self.selected_port.close()
        
    def SetPotFunctions(self, id, pot_num, pot_name): ##############################FIX THIS FUNCTION - it should check if there is already a function set for the pot and removes it from this list if there is and updates it with the new selected funciton
        selected_func = id.widget.get()
        
        if len(self.detectedPotsAndFunctions) != 0:
            for x in range(len(self.detectedPotsAndFunctions)):
                index_pot = self.detectedPotsAndFunctions[x][0] 
                try:
                    if index_pot == pot_name:
                        self.detectedPotsAndFunctions.remove(self.detectedPotsAndFunctions[x]) 
                        self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func])
                    else:
                        self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func])
                except IndexError:
                    pass
        else:
            self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func])
        print(self.detectedPotsAndFunctions)
    
    def CreatePotComboFunctionBoxes(self):
        boxes = ["Pot 1", "Pot 2", "Pot 3", "Pot 4"]
        grid_space = 0
        
        for index, name in enumerate(boxes):
            self.potbox = ttk.Combobox(self.window, values=self.all_apps)
            self.potbox.grid(row=1+grid_space, column=2)
            self.potbox.bind("<<ComboboxSelected>>", lambda id, idx=index, n=name: self.SetPotFunctions(id, idx, n))
            self.potboxlist.append(self.potbox)

            potlabel = Label(self.window, text=name)
            potlabel.grid(row=1+grid_space, column=4)
            grid_space += 4

    def StartUp():
        query_numberofPOTS = self.selected_port.send("?POTS\n")
        return query_numberofPOTS
    
    def DetectNewPrograms(self): #Constantly searches for new programs that were opened and can be controlled
        while not self.stop_event.is_set():
            self.sessions = AudioUtilities.GetAllSessions()
            self.IterateNewPrograms()
            time.sleep(2) #This function is running in a thread so waiting 2 seconds shouldn't cause any issues with the rest of the program
    
    def IterateNewPrograms(self):#Constatly updates the list of active programs and removes them once they're no longer detected running
        if not self.stop_event.is_set():
            self.all_apps = []
            self.all_apps.append('microphone')
            self.all_apps.append('master')
            try: #need this try and except block otherwise the tkinter window would crash  
                for session in self.sessions:
                        process = session.Process
                        if process:
                            process_name = process.name()
                            if process_name not in self.all_apps:
                                self.all_apps.append(process_name)
                                self.UpdateAllComboboxes()
            except Exception as e:
                print(f"HERE {e}")
    
    def UpdateAllComboboxes(self):
        for potbox in self.potboxlist:
            potbox['values'] = self.all_apps
    
    def IsWindowClosed(self):
        return self.window.winfo_exists()

    def ReadConfigFile(self):
        self.config.read(self.SetupFile)

    def set_microphone_volume(self, volume_level): #be able to set microphone level
        print(volume_level)
        # Find the microphone device
        # for device in self.devices:
        #     print(device)
        #     if device.Type == 'Capture': 
        #         print(device)
        #         # endpoint = AudioUtilities.GetDevice(device.id)
        #         # volume = endpoint.Activate(ISimpleAudioVolume, CLSCTX_ALL, None)
               
        #         # volume.SetMasterVolume(volume_level, None)
        #         # print(f"Microphone volume set to {volume_level * 100}%")
        #         # return
        # print("Microphone not found.")


OpenMixer()
