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

        self.window = Tk() #initialize window
        self.window.title("OpenMixer")
        self.center_window()
        self.stop_event = threading.Event() #This is the stop event for all the threads and helps them shut down when the program is closed
        
        self.all_apps = [] #Puts all the apps detected to be running in this list
        self.potboxlist = [] #puts the addresses of the potentiometer Tkinter Combobox objects, so they can be referenced  
        
        self.sessions = AudioUtilities.GetAllSessions() #find all active programs
    
        self.ProgramDetectionThread = threading.Thread(target=self.DetectNewPrograms) #run the function which searches for new programs in the background, so that it can always find new sessions as they are initialized (user opens another program that they want to control)
        self.ProgramDetectionThread.start()

        self.detectedPotsAndFunctions = [] #puts the functions of the potentiometers in this box. Ex: Pot 1, FireFox.exe
        self.active_ports = [] #stores all the active COM ports in this array
        
        self.config = configparser.ConfigParser() #Configparser for saving the state of the settings/preferences of the user, so they can be auto-loaded on startup
        self.SetupFileName = "OpenMixerSetup.ini"
        self.Configdata = {}
        self.config.add_section("Setup")
        
        self.SelectPortsBox = ttk.Combobox(state='readonly', values=self.active_ports, width=50) 
        self.SelectPortsBox.set('Select Port')
        self.SelectPortsBox.bind("<<ComboboxSelected>>", self.EstablishPortConnection)
        self.SelectPortsBox.grid(row=1, column=8) 

        
        self.ReadAndProcess_active = False
        
        self.Startup()
        
        self.window.protocol("WM_DELETE_WINDOW", self.Shutdown) #executes "self.shutdown" function when the window (UI) is detected as closed
        self.window.mainloop()
    
    def findAvailablePorts(self): #search for all comports and upload them to the array (this function runs in the background and will constantly search for new COMS)
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port not in self.active_ports:
                    self.active_ports.append(f"['{port.device}', '{port.description}', '{port.manufacturer}']")   
            self.SelectPortsBox['values'] = self.active_ports
    
    def changeVolume(self, app, volume_level): #Function changes the volume of the program
            try: #need this try and except block otherwise the tkinter window would crash
                for session in self.sessions: 
                    process = session.Process# Get the process associated with the session
                    if process and app.lower() in process.name().lower(): 
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        volume.SetMasterVolume(volume_level, None)# Set the volume level
                        print(f"Set volume for {app} to {volume_level * 100}%")
            except:
                pass
    
    def Return_COM_Index(self): #Returns the index of the selected COM port
            index_COM = self.SelectPortsBox.current()
            return index_COM
    
    def EstablishPortConnection(self, event): #Connect to the port the user selects, and also store that information in the configparser object to be written to the ini file later.
            try:
                set_port = self.config["Setup"]["port"]
            except KeyError:
                pass
    
            try:
                selected = self.Return_COM_Index()
                selected = self.active_ports[selected]
                selected = ast.literal_eval(selected)

                self.selected_port = serial.Serial(f"{selected[0]}", 9600)
                
                self.config.set("Setup", "Port", str(selected[0]))
                self.config.set("Setup", "port_name", str(self.selected_port.name))
                
                if self.ReadAndProcess_active == False: 
                    self.ThreadFunction(self.ReadAndProcess)
                
            except Exception as e:
                messagebox.showerror("Port Busy",message=f"Port: {selected[0]} is currently in use by another application")
                print(e)

    def ThreadFunction(self, targetFunction): #Function runs other functions in the background
        self.stop_event.clear()
        self.thread = threading.Thread(target=targetFunction) #Run the ReadAndProcess function similtaneously otherwise the tkinter window is unable to update and crashes
        self.thread.start()

    def ReadAndProcess(self): #Read the data from the arduino (COM port)
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
                            self.changeVolume(app_name, volume_value)  
                        except ValueError:
                            print(f"Error: Invalid value received: {data_to_list[pot_index]}")
                            if data_to_list[0] == "RESPONSE":
                                data_to_list.remove(data_to_list[0])
                                self.PinNumbersBox.insert("1.0", data_to_list)
                                print('inserted')
                    else:
                        print(f"Error: Index {pot_index} not in range")
                    num += 1

                except IndexError:
                    print(f"Error reading and processing data")
                    continue #IndexError is called if the user connects to the Active COM port before selecting a program to control with the pots.
               
            except AttributeError as p:
                print('line 157')
                print(p)
           
            except Exception as e:
                print(f"Unexpected Error - {e}")
                self.stop_event.set()

    def Shutdown(self): #destroys the window (UI), ends the background funcitons (threads), and writes to the config file when the UI is detected closed
        self.config.set("Setup", "Potentiometers", str(self.detectedPotsAndFunctions))
        self.WriteConfigFile()
        self.stop_event.set()
        self.window.destroy() #destroy the window before closing the threads to make it appear that the program has been closed 
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2) #wait 2 seconds to close the active threads otherwise weird errors occur
        self.selected_port.close()
        
    def SetPotFunctions(self, id, pot_num, pot_name): #set the potentiometers function
        selected_func = id.widget.get()
        
        pot_found = False
        
        for i in range(len(self.detectedPotsAndFunctions)):
            pot_index = self.detectedPotsAndFunctions[i][0]
    
            if pot_index == pot_name:
                self.detectedPotsAndFunctions[i] = [pot_name, pot_num, selected_func, str(id)]
                pot_found = True
                break
        
        if not pot_found:
            self.detectedPotsAndFunctions.append([pot_name, pot_num, selected_func, str(id)])
        
    def CreatePotComboFunctionBoxes(self): #Creates UI objects (comboboxes) for to select the potentiometers functions
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

    def DetectNewPrograms(self): #Constantly searches for new programs that were opened and can be controlled
        while not self.stop_event.is_set():
            self.sessions = AudioUtilities.GetAllSessions()
            self.IterateNewPrograms()
            time.sleep(2) #This function is running in a thread so waiting 2 seconds shouldn't cause any issues with the rest of the program
    
    def IterateNewPrograms(self):#Constatly updates the list of active programs and removes them once they're no longer detected running
        if not self.stop_event.is_set():
            self.all_apps = []              
            self.all_apps.append('master') # Set this as a default option
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

    def WriteConfigFile(self):
        with open(self.SetupFileName, "w") as settings:
            self.config.write(settings)
            print("Data written")
        
    def center_window(self):
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        width = 600
        height = 200
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def PlaceDefaultTextPotBox(self, index, preloadtext):
        combobox = self.potboxlist[index]
        combobox.set(preloadtext)

    def Startup(self): #sets up the program on initialization, like setting the previously applied settings by defauly (if any are saved)
        if os.path.exists(self.SetupFileName) == False: #check if the path exists, and if it doesn't then create it. 
            with open(self.SetupFileName, "x") as f:
                self.WriteConfigFile()
            self.CreatePotComboFunctionBoxes()
            
        else:
            self.config.read(self.SetupFileName)
            try:
                saved_port_id = self.config["Setup"]["port"]
                saved_port_name = self.config["Setup"]["port_name"]
                saved_potentiometers = self.config["Setup"]["potentiometers"]
                
                if saved_port_id != "None":
                    try: 
                        self.selected_port = self.selected_port = serial.Serial(saved_port_id, 9600)
                        self.SelectPortsBox.set(str(saved_port_name))
                        
                        self.ThreadFunction(self.ReadAndProcess)
                        self.ReadAndProcess_active = True
                    
                    except serial.SerialException: #Rasied when the COM port isn't found (ex: the device isn't plugged in).
                        self.SelectPortsBox.set(f"'{saved_port_name}' NOT FOUND")
                
                self.CreatePotComboFunctionBoxes()
                if saved_potentiometers != "None":
                    for saved_device in ast.literal_eval(saved_potentiometers):
                        self.detectedPotsAndFunctions.append([saved_device[0], saved_device[1], saved_device[2], saved_device[3]])
                        self.PlaceDefaultTextPotBox(saved_device[1], saved_device[2])
            except KeyError as e:
                print("Line 277 ", e)
                pass

        self.ThreadFunction(self.findAvailablePorts())
OpenMixer()
