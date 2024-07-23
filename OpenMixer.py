from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
from ctypes import cast, POINTER
from tkinter import *
from tkinter import ttk
#from tkinter import Canvas
import tkinter 
import serial
import serial.tools.list_ports
import ast
import threading

class OpenMixer:

    def __init__(self):
        super().__init__()
        
        self.window = Tk() #initialize window
        self.window.geometry("1000x500")#set window size in pixels
        self.window.title("OpenMixer")

        #self.bgCanvas = Canvas(self.window, bg='grey')
        #self.bgCanvas.grid(row=1, column=1)

        self.all_apps = ["Discord.exe", "Firefox.exe", "chrome.exe"]
        self.sessions = AudioUtilities.GetAllSessions()

        self.detectedPotsAndFunctions = []
        
        self.active_ports = []
        
       
             


        def findAvailiblePorts():
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.active_ports.append(f"['{port.device}', '{port.description}', '{port.manufacturer}']")

        def DrawCircles():
            pass
                  
        findAvailiblePorts()
        
        self.SelectPortsBox = ttk.Combobox(state='readonly', values=self.active_ports, width=50) 
        self.SelectPortsBox.bind("<<ComboboxSelected>>", self.EstablishPortConnection)

        self.SelectPortsBox.grid(row=5, column=5)
        
        #self.optionalMic = Button(self.window, text="Use Mic?")
        #self.optionalMic.pack() 

        #self.text_box = Label(self.window, height=1, width=8, text='Password:', font=("Helvetica", 9))
        #self.text_box.pack()       

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
        try:
            num = 0
            while True:
                read_data = self.selected_port.readlines(1)
                decode_serialtostring = read_data[0].decode()
                decode_serialtostring = ast.literal_eval(decode_serialtostring)
                self.changeVolume(self.detectedPotsAndFunctions[num][2], int(decode_serialtostring[self.detectedPotsAndFunctions[num][1]])/100)
                #print(self.detectedPotsAndFunctions[num][2], decode_serialtostring[self.detectedPotsAndFunctions[num][1]])
                #print(self.detectedPotsAndFunctions[num][2])
                num +=1
                if num == len(self.detectedPotsAndFunctions):
                     num = 0
                #self.changeVolume("Firefox.exe", int(decode_serialtostring[0])/100)
        except Exception as e:
            #print(f"Closed {self.selected_port}")
            print("ERROR" + str(e))
            num = 0
    
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

        #Ideas: Make a UI and let the user decide what apps are to control and whether or not to use their microphone and add a pause media button.
OpenMixer()