import cv2
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QVideoProbe
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QVBoxLayout


class StreamVideo_V2(QObject):
    imageSignal = pyqtSignal(object)
    startSignal = pyqtSignal()
    stopSignal = pyqtSignal()
    errorSignal = pyqtSignal(str)

    def __init__(self, rtsp=None, parent=None, x=None, y=None):
        super(StreamVideo_V2, self).__init__()
        self.parent = parent
        self.x = x
        self.y = y
        self.image = None
        self.rtsp = rtsp
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        media_content = QMediaContent(QUrl(rtsp))
        self.media_player.setMedia(media_content)
        self.video_probe = QVideoProbe()
        self.video_probe.videoFrameProbed.connect(self.on_frame_probed)
        self.video_probe.setSource(self.media_player)
        self.video_widget.setAutoFillBackground(True)
        layoutHeader = QVBoxLayout(self.parent)
        layoutHeader.setContentsMargins(0, 0, 0, 0)
        self.parent.setLayout(layoutHeader)
        self.parent.layout().addWidget(self.video_widget)
        # self.parent.setStyleSheet("background-color: black;")
        # self.parent.addLabel(self.video_widget)
        # self.parent.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.video_widget.raise_()
        # self.parent.addLabel(self.video_widget )
        # self.parent.setAutoFillBackground(True)
        # self.parent.setAttribute(Qt.WA_TransparentForMouseEvents)

        # self.video_widget.raise_()
        # set video_get_cursor

    def on_frame_probed(self, frame):
        self.imageSignal.emit(frame)

    def stop(self):
        self.media_player.stop()

    def start(self):
        self.media_player.play()
        self.video_probe.setSource(self.media_player)

    def getBackgroundBlack(self):
        image = cv2.imread("res/drawable/images/background-black.jpg")
        return image

    def getImage(self):
        return self.image

    # reload media player
    def reload(self):
        self.stop()
        self.start()
