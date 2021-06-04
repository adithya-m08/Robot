import numpy as np
import cv2
import serial

cap = cv2.VideoCapture(0)
linecolor = (100, 215, 255)
lwr_red = np.array([  9, 206, 142])
upper_red = np.array([ 29, 226 ,222])
Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
Ser.flush()

while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()
        
    frame = cv2.flip(frame, 1)
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
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            cv2.circle(frame, center, 5, linecolor, -1)
            
        if(x < 280):
            print("L")
            Ser.write(b"L")

        elif(x > 320):
            print("R")
            Ser.write(b"R")

        else:
            print("F")
            Ser.write(b"F")
        
    data,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.flip(frame, 1))
    if data!='':
        data=data.split(' - ')[1]
        if(data=='right'):
            print("shift-right")
            #addcommands
        elif(data=='left'):
            print("shift-left")
            #addcommands
        elif(data=='opposite'):
            print("shift-opposite")
            #addcommands

    cv2.imshow("Frame", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
