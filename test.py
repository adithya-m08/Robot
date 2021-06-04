import serial
Ser = serial.Serial("COM4", baudrate=9600)
Ser.flush()
while True:
    print(Ser.readline().decode().strip())