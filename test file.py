import serial
import time

def read_from_serial(port_name, baud_rate=9600, timeout=1):
    try:
        with serial.Serial(port_name, baudrate=baud_rate, timeout=timeout) as ser:
            print(f"Connected to {port_name}")

            while True:
                if ser.in_waiting > 0:
                   
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Received: {data}")
                time.sleep(1)  

    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port_name = 'COM5'
    read_from_serial(port_name)