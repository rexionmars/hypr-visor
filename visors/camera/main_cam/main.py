import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import os

os.environ['QT_QPA_PLATFORM'] = 'xcb'

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera")
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        
        # Inicializa a câmera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Erro: Não foi possível acessar a câmera.")
            return
            
        print("Câmera iniciada com sucesso!")
        print("Feche a janela para sair.")
        
        # Configura o timer para atualizar os frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~33 fps
        
        # Configura o evento de fechamento da janela
        self.destroyed.connect(self.cleanup)
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Converte o frame para RGB e cria uma QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_image))
            
    def cleanup(self):
        self.cap.release()

def acessar_camera():
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    acessar_camera()