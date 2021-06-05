import numpy as np
import cv2
import serial

cap = cv2.VideoCapture(0)
linecolor = (100, 215, 255)
lwr_red = np.array([7, 245, 132])
upper_red = np.array([27, 255, 212])
lwr_black = np.array([0,0,0])
upper_black = np.array([10,10,40])
lwr_violet = np.array([120,230,49])
upper_violet = np.array([146,255,129])
lwr_pink = np.array([152,86,171])
upper_pink = np.array([183,264,289])


Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
Ser.flush()

def laneShift(dir):
    while True:
        ret, frame = cap.read()
        if not ret:
            _,frame=cap.read()
        cv2.imshow('Shifting',frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.inRange(hsv, lwr_red, upper_red)
        mask = cv2.dilate(mask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        center = None

        Ser.write(b'f')

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if radius > 2:
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
                cv2.circle(frame, center, 2, linecolor, -1)
            
            if y > 450:
                #move a bit more then stop
                #Ser.write(b'f')
                if(dir == 'r'):
                    #turn 90 degrees anticlock and resume
                    #Ser.write(b'l')
                    cv2.destroyWindow("Shifting")
                    return
                elif(dir == 'l'):
                    #turn 90 degrees clock and resume
                    #Ser.write(b'r')
                    cv2.destroyWindow("Shifting")
                    return
                    
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyWindow("Shifting")
            break


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
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            cv2.circle(frame, center, 5, linecolor, -1)
            
        if(x < 280):
            print("L")
            Ser.write(b"l")

        elif(x > 320):
            print("R")
            Ser.write(b"r")

        else:
            print("F")
            Ser.write(b"f")

    else:
        print("Track Not Visible")



    black_mask = cv2.inRange(hsv, lwr_black, upper_black)
    violet_mask = cv2.inRange(hsv, lwr_violet, upper_violet)
    pink_mask = cv2.inRange(hsv, lwr_pink, upper_pink)


    if(cv2.countNonZero(black_mask)>2000000000000):
        print("shift-right")
        laneShift('r')
    elif(cv2.countNonZero(violet_mask)>200):
        print("shift-left")
        laneShift('l')
    elif(cv2.countNonZero(pink_mask)>200):
        print("shift-opposite")
        #commands to move to the center


    cv2.imshow("Frame", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        Ser.close()
        cv2.destroyAllWindows()
        break
