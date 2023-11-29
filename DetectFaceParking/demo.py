import cv2

cap = cv2.VideoCapture("rtsp://admin:Oryza@123@192.168.111.252:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif")

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("error")
        break

cap.release()
cv2.destroyAllWindows()