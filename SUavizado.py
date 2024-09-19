import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QComboBox, QWidget, QFileDialog
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Suavizado y Bordes - OpenCV y PyQt6')
        self.setGeometry(100, 100, 800, 600)
        self.image_path = None
        self.image = None
        self.image_suavizada = None
        self.image_bordes = None
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)
        self.ax1, self.ax2, self.ax3 = self.canvas.figure.subplots(1, 3)
        self.suavizado_dropdown = QComboBox(self)
        self.suavizado_dropdown.addItems([str(i) for i in range(1, 10)])
        self.suavizado_dropdown.currentIndexChanged.connect(self.update_image)
        self.layout.addWidget(self.suavizado_dropdown)
        self.load_button = QPushButton('Cargar Imagen', self)
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button)
        self.save_button = QPushButton('Guardar Imagen Suavizada', self)
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Images (*.png *.xpm *.jpg *.jpeg)"])
        if file_dialog.exec():
            self.image_path = file_dialog.selectedFiles()[0]
            self.image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            self.update_image()

    def update_image(self):
        if self.image is not None:
            suavizado_valor = int(self.suavizado_dropdown.currentText())
            suavizado = np.ones((3, 3), np.float32) / suavizado_valor
            self.image_suavizada = cv2.filter2D(self.image, -1, suavizado)
            bordes_sobel = np.array(
                [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
            self.image_bordes = cv2.filter2D(self.image, -1, bordes_sobel)
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax1.imshow(self.image, cmap='gray')
            self.ax1.set_title("Original")
            self.ax2.imshow(self.image_suavizada, cmap='gray')
            self.ax2.set_title("Suavizada")
            self.ax3.imshow(self.image_bordes, cmap='gray')
            self.ax3.set_title("Bordes")
            self.canvas.draw()

    def save_image(self):
        if self.image_suavizada is not None:
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilters(["Images (*.png *.jpg *.jpeg)"])
            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                cv2.imwrite(save_path, self.image_suavizada)


app = QApplication(sys.argv)
window = ImageApp()
window.show()
sys.exit(app.exec())
