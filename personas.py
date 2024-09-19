import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Detección de Rostros - OpenCV y PyQt6')
        self.setGeometry(100, 100, 800, 600)
        self.image_path = None
        self.image = None
        self.image_rostros = None
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)
        self.ax1, self.ax2 = self.canvas.figure.subplots(1, 2)
        self.load_button = QPushButton('Cargar Imagen', self)
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button)
        self.save_button = QPushButton(
            'Guardar Imagen con Rostros Detectados', self)
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Images (*.png *.xpm *.jpg *.jpeg)"])
        if file_dialog.exec():
            self.image_path = file_dialog.selectedFiles()[0]
            self.image = cv2.imread(self.image_path)
            self.apply_face_detection()

    def apply_face_detection(self):
        if self.image is not None:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            rostros = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            self.image_rostros = self.image.copy()
            for (x, y, w, h) in rostros:
                cv2.rectangle(self.image_rostros, (x, y),
                              (x+w, y+h), (255, 0, 0), 2)

            self.ax1.clear()
            self.ax2.clear()
            self.ax1.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
            self.ax1.set_title("Original")
            self.ax2.imshow(cv2.cvtColor(
                self.image_rostros, cv2.COLOR_BGR2RGB))
            self.ax2.set_title("Detección de Rostros")
            self.canvas.draw()

    def save_image(self):
        if self.image_rostros is not None:
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilters(["Images (*.png *.jpg *.jpeg)"])
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                cv2.imwrite(save_path, self.image_rostros)


app = QApplication(sys.argv)
window = ImageApp()
window.show()
sys.exit(app.exec())
