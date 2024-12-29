# OpenMixer
DIY volume control sliders for applications on your PC.

# How It Works

OpenMixer operates with two main components that communicate over a serial connection to manage your PC's audio settings:

1. Arduino Code: This is uploaded to the Arduino microcontroller. The microcontroller reads the values from the connected potentiometers (sliders/knobs) and sends this data via serial (over USB) to the PC.

2. Python Software: This runs on your PC and listens for the data sent from the Arduino. Based on the received values, it adjusts the volume of the selected application.

# Setup Instructions

1. Connect the Potentiometers: Wire your potentiometers to the Arduino according to the circuit diagram provided.

2. Upload the Arduino Code: Use the Arduino IDE to upload the provided code to your Arduino.

3. Install Python and Dependencies: Make sure you have Python installed on your PC. Install the required Python packages using the provided requirements file.

4. Run the Python Software: Start the Python software, and it will begin communicating with the Arduino to control the volume of your applications.

# Customization

This project was built in my spare time, so it may not be packed with advanced features. However, if you have the technical skills, feel free to modify and extend the software to fit your needs. You can customize the code to adjust different aspects of the volume control or integrate additional features.

# Disclaimer
This project was developed as a personal project. It may require adjustments based on your specific setup and preferences.



