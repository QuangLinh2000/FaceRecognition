import os
import time

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow
import torch
from dotenv import load_dotenv
from torchvision import transforms as trans
from res.MainLayout import Ui_MainWindow
from src.utils.mainModel import loadModel, compare
from src.model.FaceIdAuth import FaceIdAuth
from src.service.FaceIdAuthService import FaceIdAuthService
from src.service.SocketClientApp import SocketClientApp


class MainWindowActivity(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindowActivity, self).__init__()
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setupUi(self)
        load_dotenv()
        # self.showMaximized()
        from src.utils.StreamVideo_V2 import StreamVideo_V2
        from src.utils.BaseFaceAligner import FaceAligner
        from src.utils.YOLOv8_face import YoloMask
        from ultralytics import YOLO

        self.streamVideoLeftLeft = StreamVideo_V2(
            rtsp=os.getenv('RTSP'),
            parent=self.videoFrame)
        self.streamVideoLeftLeft.start()
        self.streamVideoLeftLeft.imageSignal.connect(self.update_frameLeftLeft)
        self.timeStart = time.time()
        self.model = YOLO('Weights/yolov8n-face.torchscript', task='pose')
        self.yoloMask = YoloMask()
        self.track_idsOld = []
        self.nameR = []
        self.score_100R = []
        self.faceIdAuthService = FaceIdAuthService()
        self.check_read_card = True

        self.test_transform = trans.Compose([
            trans.ToTensor(),
            trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])])
        self.detect_model = loadModel()
        self.faceAligner = FaceAligner()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.host = os.getenv('HOST_SOCKET')
        self.port = os.getenv('PORT_SOCKET')
        self.socketClientApp = SocketClientApp.getInstance(self.host, self.port)
        self.socketClientApp.status_read_card_signal.connect(self.update_status_read_card)
        self.doubleSpinBox.setValue(0.5)
        self.count = 0
        self.oldNameSearch = ""

        self.timer = QTimer()
        self.timer.setInterval(60000)
        self.timer.timeout.connect(self.connectSocketClound)
        self.timer.start()

    def connectSocketClound(self):
        if self.socketClientApp.isConnect is False:
            self.socketClientApp.sio.disconnect()
            self.socketClientApp.sio.connect('http://{}:{}'.format(self.host, self.port))

    def update_status_read_card(self, data):
        # {'position': 'LEFT', 'result': False}
        if data["result"] is False:
            self.check_read_card = True

    def update_frameLeftLeft(self, frame):
        timeDelay = self.doubleSpinBox.value()
        if time.time() - self.timeStart > timeDelay:
            self.timeStart = time.time()
            frame = self.convertQImageToMat(frame)
            results = self.model.track(frame, persist=True, imgsz=640, verbose=False, conf=0.6)
            boxesR = results[0].boxes.xywh.cpu()
            boxes, scores, kpts = self.yoloMask.detect(frame, results)

            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()
            else:
                track_ids = [0] * len(boxesR)

            isUpdate = False
            for i in range(len(track_ids)):
                if track_ids[i] not in self.track_idsOld and track_ids[i] != 0:
                    isUpdate = True
                    break
            if len(track_ids) > len(self.track_idsOld):
                isUpdate = True
            self.track_idsOld = track_ids

            if isUpdate or "" in self.nameR:
                self.check_read_card = True
                self.oldNameSearch = ""
                self.count = 0
                data = self.faceIdAuthService.getAll(FaceIdAuth)
                self.nameR = []
                self.score_100R = []
                for box, score, kp in zip(boxes, scores, kpts):
                    aface, M = self.faceAligner.align(frame, box, kp)
                    name = ""
                    scoreTemp = 0
                    for item in data:
                        feature_vector = np.frombuffer(item.Encoding, dtype=np.float32).copy()
                        database_embs = torch.from_numpy(feature_vector)
                        em = self.detect_model(self.test_transform(aface).to(self.device).unsqueeze(0))
                        s, r, s100 = compare([database_embs], [em])
                        if r[0] == 0:
                            name = item.CardNumber
                            scoreTemp = s100[0]
                            break

                    self.nameR.append(name)
                    self.score_100R.append(scoreTemp)
            t = ""
            nameSearch = ""
            for name, score in zip(self.nameR, self.score_100R):
                t += name + " " + ' score:{:.0f}'.format(score) + "\n"
                if name != "":
                    nameSearch = name

            if len(nameSearch) > 0 and nameSearch != "" and self.check_read_card is True and self.count < 5:
                if self.oldNameSearch != nameSearch:
                    self.oldNameSearch = nameSearch
                    self.count = 0
                else:
                    self.count += 1

                self.check_read_card = False
                if self.socketClientApp.isConnect:
                    position = "LEFT"
                    if self.radioButtonRight.isChecked():
                        position = "RIGHT"
                    self.socketClientApp.sio.emit("authentication", {"position": position, "data": nameSearch})

            self.labelResult.setText(t)

    def convertQImageToMat(self, incomingImage):
        '''  Converts a QImage into an OpenCV Mat format  '''
        # Convert to a QImage format suitable for conversion to OpenCV Mat
        incomingImage = incomingImage.image()
        incomingImage = incomingImage.convertToFormat(QImage.Format_RGB888)

        # conver to rgb
        incomingImage = incomingImage.rgbSwapped()
        # incomingImage = convert_to_rgb(incomingImage)

        width = incomingImage.width()
        height = incomingImage.height()
        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 3)  # Converts to 3-channel (BGR) Mat
        return arr


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mainWindow = MainWindowActivity()
    mainWindow.show()
    sys.exit(app.exec_())
