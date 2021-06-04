import numpy as np
import cv2
import serial

cap = cv2.VideoCapture(0)

linecolor = (100, 215, 255)
lwr_red = np.array([7, 245, 132])
upper_red = np.array([27, 255, 212])
Ser = serial.Serial("COM4", baudrate=9600)
Ser.flush()

while True:
    ret, frame = cap.read()
    if not ret:
        _,frame=cap.read()
    cv2.imshow("vid",frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.inRange(hsv, lwr_red, upper_red)
    mask = cv2.dilate(mask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center = None
    cv2.imshow("mask",mask)
    Ser.write(b'F')

    if len(cnts) > 0: #keep robot moving front regardless of len(cnts) value after turning
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 2:
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            cv2.circle(frame, center, 2, linecolor, -1)
        print(y)
        if y > 450:
            #move a bit more then stop
            Ser.write(b'l')
            break

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        Ser.close()
        cv2.destroyAllWindows()
        break