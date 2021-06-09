import numpy as np
import cv2
import serial
import time

flag,flag1,object=0,0,None
cap = cv2.VideoCapture(0)
width=cap.get(3)
height=cap.get(4)

configPath = 'resources/config.pbtxt'
weightsPath = 'resources/weights.pb'

linecolor = (100, 215, 255)
lwr_red = np.array([9, 206, 142])
upper_red = np.array([29, 226 ,222])

classNames= []
classFile = 'resources/object.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Ser = serial.Serial("/dev/ttyACM0", baudrate=9600)
# Ser.flush()

##### QR Code Detection #####

print('\n\tWaiting for QR Code\n')
while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()

    cv2.imshow("QR",frame)
    objects,_,_=cv2.QRCodeDetector().detectAndDecode(frame)
    
    if objects!='':
        objects=list(map(str.strip,objects.split(',')))
        cv2.destroyWindow("QR")
        break

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cv2.destroyWindow("QR")
        break

print(objects)

#### Navigation and Object Detection ####

print("\n\tNavigating Tracks\n")
while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()
    cv2.imshow("Navigaation",frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.inRange(hsv, lwr_red, upper_red)
    mask = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #center = None
    

    if( len(cnts) > 0 and flag==0):
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cv2.circle(frame, center, 5, linecolor, -1)
            
        if(x < 0.25*width):
            print("L")

        elif(x > 0.75*width):
            print("R")

        else:
            print("F")

    if(flag==1):
        #Ser.write(b'llll')

        classIds, confs, bbox = net.detect(frame,0.4)
        bbox = list(bbox)
        confs = list(np.array(confs).reshape(1,-1)[0])
        confs = list(map(float,confs))
        indices = cv2.dnn.NMSBoxes(bbox,confs,0.4,0.2)

        for i in indices:
            i = i[0]
            object=classNames[classIds[i][0]-1]
            box = bbox[i]
            x,y,w,h = box[0],box[1],box[2],box[3]
            cv2.rectangle(frame, (x,y),(x+w,h+y), color=(0, 255, 0), thickness=2)
            cv2.putText(frame,object.upper(),(box[0]+10,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                

            if(object in objects and object!='person' and flag1==0):
                print('Found',object)
                flag1=1
                time.sleep(1)
                print("\t\t\nWaiting for Thumbs Up\n")

            elif(object=='person' and flag1==1):
                print('\t\t\nThumbs Up!\n')
                time.sleep(1)
                flag,flag1=0,0
                break

    if cv2.waitKey(10) & 0xFF == ord('o'):
        flag=1
        print("\t\t\nWaiting for Object\n")