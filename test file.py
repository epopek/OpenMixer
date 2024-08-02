from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

def set_microphone_volume(volume_level):
    # Get the device enumerator
    devices = AudioUtilities.GetAllDevices()
    
    # Loop through the devices to find the microphone
    for device in devices:
        if device.FriendlyName.startswith('Microphone'):
            # Get the IAudioEndpointVolume interface for the device
            volume_control = device.Activate(IAudioEndpointVolume, CLSCTX_ALL, None)
            volume_control.SetMasterVolumeLevelScalar(volume_level, None)
            print(f"Microphone volume set to {volume_level * 100}%")
            return
    print("Microphone not found.")

# Set the microphone volume to 50%
set_microphone_volume(0.5)