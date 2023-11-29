import threading
from time import sleep

import socketio
from PyQt5.QtCore import QObject, pyqtSignal

class SocketClientApp(QObject):
    __instance = None
    isConnect = False
    status_read_card_signal = pyqtSignal(object)


    @staticmethod
    def getInstance(host=None, port=None):
        if SocketClientApp.__instance == None:
            SocketClientApp.__instance = SocketClientApp(host, port)
        return SocketClientApp.__instance

    def __init__(self, host, port):
        super(SocketClientApp, self).__init__()
        if SocketClientApp.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SocketClientApp.__instance = self
            self.host = host
            self.port = port
            self.sio = socketio.Client()
            self.sio.on('connect', self.connect)
            self.sio.on('connect_error', self.on_connect_error)
            self.sio.on('disconnect', self.disconnect)
            self.sio.on('result_authentication', self.status_read_card)
            self.isConnect = False

            threading.Thread(target=self.start_event, daemon=True).start()

    def status_read_card(self,data):
        self.status_read_card_signal.emit(data)

    def start_event(self):
        while True:
            try:
                self.sio.connect('http://{}:{}'.format(self.host, self.port))
                self.isConnect = True
                break
            except:
                # print('ket noi that bai', 'http://{}:{}'.format(self.host, self.port))
                sleep(1)
                continue

    def connect(self):
        print('ket noi den server trong bai xe thanh cong')
        self.isConnect = True
        # join room

    def disconnect(self):
        print('disconnected voi server trong bai xe')
        self.isConnect = False

    def on_connect_error(self, data):
        # print("ket noi that bai voi server trong bai xe")
        self.isConnect = False


