import numpy as np
import cv2
import serial
import time

flag1,flag2,flag3,c1=0,0,0,0
cap = cv2.VideoCapture(0)
width=cap.get(3)
height=cap.get(4)

linecolor = (100, 215, 255)

lwr_red = np.array([7, 171, 132])
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
    center = None
    
    if( len(cnts) > 0):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 3:
            cv2.circle(frame, center, 5, linecolor, -1)
            
        if(x <0.2*width):
            print("L")
            Ser.write(b"l")

        elif(x > 0.8*width):
            print("R")
            Ser.write(b"r")

        else:
            print("F")
            Ser.write(b"ff")

    else:
        print("Track Not Visible")
        c1+=1
        if(c1==5):
            Ser.write(b'b')
            c1=0

    green_mask = cv2.inRange(hsv, lwr_green, upper_green)
    violet_mask = cv2.inRange(hsv, lwr_violet, upper_violet)
    pink_mask = cv2.inRange(hsv, lwr_pink, upper_pink)

    if(cv2.countNonZero(green_mask)>1000 and flag1==0):
        flag1=1
        print("shift-right")
        #time.sleep(1)
        Ser.write(b'rrrrrrffffffffffffffffflllllllll')
        time.sleep(5)

    elif(cv2.countNonZero(violet_mask)>1000 and flag2==0):
        flag2=1
        print("shift-left")
        #time.sleep(1)
        Ser.write(b'llllllllllffffffffffffrrrrrrrrr')
        time.sleep(4)
        

    elif(cv2.countNonZero(pink_mask)>1000 and flag3==0):
        flag3=1
        print("shift-opposite")
        Ser.write(b'lllllllllllllllllllllfffffffffffffffffffffffffffffffffffffff')
        time.sleep(5)
        break

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        Ser.close()
        cv2.destroyAllWindows()
        break