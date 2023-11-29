import time

import cv2
from ultralytics import YOLO
# Load the YOLOv8 model
model = YOLO('yolov8n.engine',task='detect')

image = cv2.imread('logo_parking_face.png')

for i in range(10):
    st =time.time()
    model.predict(image, )
    print(time.time() - st)