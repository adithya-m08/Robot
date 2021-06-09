import numpy as np
import cv2
import serial
import time

flag=0
cap = cv2.VideoCapture(0)
width=cap.get(3)
height=cap.get(4)

linecolor = (100, 215, 255)

lwr_red = np.array([7, 245, 132])
upper_red = np.array([27, 255, 212])

lwr_green = np.array([68, 142, 74])
upper_green = np.array([88, 162, 154])

lwr_violet = np.array([108,193,52])
upper_violet = np.array([131,255,159])

lwr_pink = np.array([161,134,176])
upper_pink = np.array([179,171,255])

Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
Ser.flush()

while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()

    cv2.imshow("Frame", frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.inRange(hsv, lwr_red, upper_red)
    mask = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    if( len(cnts) > 0 and flag!=1):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 3:
            cv2.circle(frame, center, 5, linecolor, -1)
            
        if(x < 0.25*width):
            print("L")
            Ser.write(b"l")

        elif(x > 0.75*width):
            print("R")
            Ser.write(b"r")

        else:
            print("F")
            Ser.write(b"f")

    else:
        print("Track Not Visible")

    green_mask = cv2.inRange(hsv, lwr_green, upper_green)
    violet_mask = cv2.inRange(hsv, lwr_violet, upper_violet)
    pink_mask = cv2.inRange(hsv, lwr_pink, upper_pink)

    if(cv2.countNonZero(green_mask)/(width*height)>0.3 and flag==0):
        flag=1
        print("shift-right")
        Ser.write(b'rrrrrfffffffflllll')
        time.sleep(1)
        flag=0

    elif(cv2.countNonZero(violet_mask)/(width*height)>0.3 and flag==0):
        flag=1
        print("shift-left")
        Ser.write(b'lllllffffffffrrrrr')
        time.sleep(1)
        flag=0

    elif(cv2.countNonZero(pink_mask)/(width*height)>0.3 and flag==0):
        flag=1
        print("shift-opposite")
        Ser.write(b'llllllllllllllll')
        Ser.write(b'ffffffffff')
        time.sleep(1)
        flag=0

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        Ser.close()
        cv2.destroyAllWindows()
        break