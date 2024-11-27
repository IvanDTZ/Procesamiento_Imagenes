import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesador de Imágenes en Escala de Grises")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_btn = QPushButton("Cargar Imagen", self)
        self.erosion_btn = QPushButton("Aplicar Erosión", self)
        self.dilation_btn = QPushButton("Aplicar Dilatación", self)
        self.clean_noise_btn = QPushButton(
            "Proceso de Limpieza de Ruido", self)
        self.edge_detection_btn = QPushButton("Detectar Bordes", self)

        self.load_btn.clicked.connect(self.load_image)
        self.erosion_btn.clicked.connect(self.apply_erosion)
        self.dilation_btn.clicked.connect(self.apply_dilation)
        self.clean_noise_btn.clicked.connect(self.clean_noise)
        self.edge_detection_btn.clicked.connect(self.edge_detection)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.erosion_btn)
        layout.addWidget(self.dilation_btn)
        layout.addWidget(self.clean_noise_btn)
        layout.addWidget(self.edge_detection_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image = None

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            self.display_image(self.image)

    def display_image(self, img):
        qformat = QImage.Format.Format_Grayscale8 if len(
            img.shape) == 2 else QImage.Format.Format_RGB888
        qimg = QImage(img.data, img.shape[1],
                      img.shape[0], img.strides[0], qformat)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap.scaled(self.label.size(
        ), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def apply_erosion(self):
        if self.image is not None:
            kernel = np.ones((5, 5), np.uint8)
            eroded_image = cv2.erode(self.image, kernel, iterations=1)
            self.display_image(eroded_image)
            cv2.imwrite("erosion_result.png", eroded_image)

    def apply_dilation(self):
        if self.image is not None:
            kernel = np.ones((5, 5), np.uint8)
            dilated_image = cv2.dilate(self.image, kernel, iterations=1)
            self.display_image(dilated_image)
            cv2.imwrite("dilation_result.png", dilated_image)

    def clean_noise(self):
        if self.image is not None:
            kernel = np.ones((5, 5), np.uint8)
            eroded = cv2.erode(self.image, kernel, iterations=1)
            cleaned_image = cv2.dilate(eroded, kernel, iterations=1)
            self.display_image(cleaned_image)
            cv2.imwrite("clean_noise_result.png", cleaned_image)

    def edge_detection(self):
        if self.image is not None:
            kernel = np.ones((5, 5), np.uint8)
            dilated = cv2.dilate(self.image, kernel, iterations=1)
            edge_image = cv2.erode(dilated, kernel, iterations=1)
            self.display_image(edge_image)
            cv2.imwrite("edge_detection_result.png", edge_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
