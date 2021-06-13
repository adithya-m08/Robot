import numpy as np
import cv2
import serial
import time

cap = cv2.VideoCapture(0)
c1=0
linecolor = (100, 215, 255)
lwr_red = np.array([7, 171, 132])
upper_red = np.array([27, 255, 212])

Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
Ser.flush()
width=cap.get(3)

while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.inRange(hsv, lwr_red, upper_red)
    mask = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center = None
    
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 3:
            #cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            cv2.circle(frame, center, 5, linecolor, -1)
        
        if(x>0 and x<=0.25*width):
            print("LLL")
            Ser.write(b"l")
            time.sleep(0.01)
            
        elif(x >0.25*width and x<=0.75*width):
            print('F')
            Ser.write(b'f')
            time.sleep(0.01)
            
        elif(x >0.75*width and x<=width):
            print("RRR")
            Ser.write(b"r")
            time.sleep(0.01)
    else:
        print("Track Not Visible")
        c1+=1
        if(c1==5):
            Ser.write(b'b')
            c1=0
        
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        Ser.close()
        cv2.destroyAllWindows()
        break
