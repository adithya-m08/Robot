import numpy as np
import cv2
import serial
import time

thres = 0.45
nms_threshold = 0.2
cap = cv2.VideoCapture(0)
flag,object=0,None

configPath = 'resources\\config.pbtxt'
weightsPath = 'resources\\weights.pb'

linecolor = (100, 215, 255)
lwr_red = np.array([9, 206, 142])
upper_red = np.array([29, 226 ,222])

classNames= []
classFile = 'resources\\object.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
Ser.flush()

##### QR Code Detection #####

while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()

    objects,_,_=cv2.QRCodeDetector().detectAndDecode(frame)
    
    if objects!='':
        objects=list(map(str.strip,objects.split(',')))
        cv2.destroyWindow("QR")
        break

    cv2.imshow("QR",frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cv2.destroyWindow("QR")
        break

print(objects)

#### Navigation and Object Detection ####

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
    
    if(len(cnts) > 0 and flag==0):
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
    
    if(Ser.in_waiting and flag!=1):
        flag=int(Ser.readline().decode().strip())
    
    if(flag==1):
        #Ser.write(b'llll')
        print("Waiting for Object")

        classIds, confs, bbox = net.detect(frame,confThreshold=thres)
        bbox = list(bbox)
        confs = list(np.array(confs).reshape(1,-1)[0])
        confs = list(map(float,confs))
        indices = cv2.dnn.NMSBoxes(bbox,confs,thres,nms_threshold)

        for i in indices:
            i = i[0]  
            object=classNames[classIds[i][0]-1]    

            if(object in objects and object!='person'):
                print('Found',object)

            elif(object=='person'):
                print('Loaded')
                #time.sleep(5)
                #Ser.write(b"rrrr")
                flag=0
                break
            

    cv2.imshow("Frame", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        Ser.write(b"s")
        Ser.close()
        cv2.destroyAllWindows()
        break