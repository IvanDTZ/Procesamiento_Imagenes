import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSlider, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap


class HSVAdjuster(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.hsv_image = None
        self.current_image = None

        self.setWindowTitle("HSV Adjuster")
        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button)

        # Barra deslizante para ajustar la tonalidad (Hue) de la imagen
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(0, 179)
        self.hue_slider.valueChanged.connect(self.update_image)
        self.layout.addWidget(self.hue_slider)

        # Barra deslizante para ajustar la saturación (Saturation) de la imagen
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 255)
        self.saturation_slider.valueChanged.connect(self.update_image)
        self.layout.addWidget(self.saturation_slider)

        # Barra deslizante para ajustar el brillo (Value) de la imagen
        self.value_slider = QSlider(Qt.Orientation.Horizontal)
        self.value_slider.setRange(0, 255)
        self.value_slider.valueChanged.connect(self.update_image)
        self.layout.addWidget(self.value_slider)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg)")
        if file_path:
            self.image = cv2.imread(file_path)
            self.hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            self.current_image = self.hsv_image.copy()
            self.update_image()

    def update_image(self):
        if self.image is not None:
            h = self.hue_slider.value()
            s = self.saturation_slider.value()
            v = self.value_slider.value()

            modified_image = self.hsv_image.copy()
            modified_image[:, :, 0] = np.clip(
                modified_image[:, :, 0] + (h - modified_image[:, :, 0]), 0, 179)
            modified_image[:, :, 1] = np.clip(
                modified_image[:, :, 1] * (s / 255.0), 0, 255)
            modified_image[:, :, 2] = np.clip(
                modified_image[:, :, 2] * (v / 255.0), 0, 255)

            bgr_image = cv2.cvtColor(modified_image, cv2.COLOR_HSV2BGR)
            height, width, channel = bgr_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(bgr_image.data, width, height,
                             bytes_per_line, QImage.Format.Format_BGR888)
            self.image_label.setPixmap(QPixmap.fromImage(q_image))

    def save_image(self):
        if self.image is not None:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "Images (*.png *.xpm *.jpg)")
            if filename:
                bgr_image = cv2.cvtColor(self.current_image, cv2.COLOR_HSV2BGR)
                cv2.imwrite(filename, bgr_image)


app = QApplication([])
window = HSVAdjuster()
window.show()
app.exec()
