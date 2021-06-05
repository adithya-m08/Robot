import serial
Ser = serial.Serial("COM4", baudrate=9600)
Ser.flush()
while True:
    print(int(Ser.readline().decode().strip()))