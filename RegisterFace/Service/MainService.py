import uuid

from Service.FaceDetectService import FaceDetectService
from Service.FaceIdAuthService import FaceIdAuthService
from Service.maskofface import mask_faces
import os

import cv2
import numpy as np
from flask import Flask, request, jsonify

from Service.BaseFaceAligner import FaceAligner
from Service.YOLOv8_face import YoloMask
from models.FaceIdAuth import FaceIdAuth


def checkFace(request):
    try:
        if 'file' not in request.files:
            return "no file"
        file = request.files['file']
        cardNumber = request.form.get('CardNumber')
        if cardNumber is None:
            return "no card number"

        # CONVERT file to image cv2
        npimg = np.fromfile(file, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        # get real path
        pathModel = "weights/yolov8n-face.pt"
        yolo = YoloMask.getInstance(path=pathModel)
        bounding_boxes, conf, faces = yolo.detect(img)
        if len(faces) == 0:
            return "no face"

        if len(faces) > 1:
            return "many face"
            # return jsonify({'status': False, 'error': 'many face'}), 400
        return cardNumber, img, bounding_boxes, faces
    except Exception as e:
        print(e)
        return "error"


def createFace(cardNumber, img, bounding_boxes, faces):
    try:
        urlImage = "data/" + cardNumber + ".jpg"
        cv2.imwrite(urlImage, img)

        faceIdAuthService = FaceIdAuthService.getInstance()
        faceAligner = FaceAligner.getInstance()
        faceDetectService = FaceDetectService.getInstance()
        afaceEmty, M = faceAligner.align(img, bounding_boxes[0], faces[0])
        emEmty = faceDetectService.convertToNumpy(afaceEmty, True)
        masks = mask_faces(img, pattern=None, pattern_weight=0.5, color=None, color_weight=0.5, code=None,
                           verbose=False, write_original_image=False)
        id = uuid.uuid4().hex
        faceIdAuth = FaceIdAuth(ID=id, CardNumber=cardNumber, Encoding=emEmty, UrlImage=urlImage)
        faceIdAuthService.create(faceIdAuth)
        # save image
        for i in range(len(masks)):
            mask = masks[i]
            aface, M = faceAligner.align(mask, bounding_boxes[0], faces[0])
            em = faceDetectService.convertToNumpy(aface, True)
            id = uuid.uuid4().hex
            faceIdAuth = FaceIdAuth(ID=id, CardNumber=cardNumber, Encoding=em, UrlImage=urlImage)
            faceIdAuthService.create(faceIdAuth)

        return True
    except Exception as e:
        print(e)
        return False
