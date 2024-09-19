import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QFileDialog, QScrollArea, QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from matplotlib import pyplot as plt


class ImageProcessingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesamiento de Imágenes")
        self.init_ui()
        self.load_image()

    def init_ui(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)

        self.original_title = QLabel("Imagen Original", self)
        self.log_title = QLabel("Transformación Logarítmica", self)
        self.gamma_title = QLabel("Transformación Gamma", self)
        self.hist_title = QLabel("Histograma", self)

        self.original_label = QLabel(self)
        self.log_label = QLabel(self)
        self.gamma_label = QLabel(self)
        self.hist_label = QLabel(self)

        self.btn_save_original = QPushButton("Guardar Imagen Original", self)
        self.btn_save_log = QPushButton(
            "Guardar Transformación Logarítmica", self)
        self.btn_save_gamma = QPushButton("Guardar Transformación Gamma", self)
        self.btn_save_hist = QPushButton("Guardar Histograma", self)

        self.btn_save_original.clicked.connect(self.save_original_image)
        self.btn_save_log.clicked.connect(self.save_log_image)
        self.btn_save_gamma.clicked.connect(self.save_gamma_image)
        self.btn_save_hist.clicked.connect(self.save_hist_image)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.original_title)
        top_row_layout.addWidget(self.log_title)

        top_row_image_layout = QHBoxLayout()
        top_row_image_layout.addWidget(self.original_label)
        top_row_image_layout.addWidget(self.log_label)

        top_row_button_layout = QHBoxLayout()
        top_row_button_layout.addWidget(self.btn_save_original)
        top_row_button_layout.addWidget(self.btn_save_log)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(self.gamma_title)
        bottom_row_layout.addWidget(self.hist_title)

        bottom_row_image_layout = QHBoxLayout()
        bottom_row_image_layout.addWidget(self.gamma_label)
        bottom_row_image_layout.addWidget(self.hist_label)

        bottom_row_button_layout = QHBoxLayout()
        bottom_row_button_layout.addWidget(self.btn_save_gamma)
        bottom_row_button_layout.addWidget(self.btn_save_hist)

        container_layout.addLayout(top_row_layout)
        container_layout.addLayout(top_row_image_layout)
        container_layout.addLayout(top_row_button_layout)

        container_layout.addLayout(bottom_row_layout)
        container_layout.addLayout(bottom_row_image_layout)
        container_layout.addLayout(bottom_row_button_layout)

        scroll_area.setWidget(container_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Cargar Imagen", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.image = cv2.imread(file_name)
            self.display_image(self.image, self.original_label)
            self.apply_log_transform()
            self.apply_gamma_transform()
            self.generate_histogram()

    def resize_image(self, img):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        max_width = screen_geometry.width() * 0.4
        max_height = screen_geometry.height() * 0.4
        height, width = img.shape[:2]
        scaling_factor = min(max_width / width, max_height / height)
        if scaling_factor < 1:
            img = cv2.resize(img, (int(width * scaling_factor),
                             int(height * scaling_factor)))
        return img

    def display_image(self, img, label):
        img = self.resize_image(img)
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line,
                       QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def apply_log_transform(self):
        img_float = np.float32(self.image) + 1
        max_value = np.max(img_float)
        if max_value == 0:
            max_value = 1
        c = 255 / np.log(1 + max_value)
        log_image = c * (np.log(img_float + 1))
        log_image[np.isnan(log_image)] = 0
        log_image[np.isinf(log_image)] = 255
        log_image = np.clip(log_image, 0, 255)
        log_image = np.array(log_image, dtype=np.uint8)
        self.display_image(log_image, self.log_label)
        self.log_image = log_image

    def apply_gamma_transform(self):
        gamma = 2.2
        gamma_image = np.array(255 * (self.image / 255)
                               ** gamma, dtype='uint8')
        self.display_image(gamma_image, self.gamma_label)
        self.gamma_image = gamma_image

    def generate_histogram(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        plt.hist(gray.ravel(), 256, [0, 256])
        plt.savefig("histogram.png")
        plt.close()
        hist_img = cv2.imread("histogram.png")
        self.display_image(hist_img, self.hist_label)
        self.hist_img = hist_img

    def save_image(self, image, default_name):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Guardar Imagen", default_name, "PNG (*.png);;JPEG (*.jpg)")
        if file_name:
            cv2.imwrite(file_name, image)

    def save_original_image(self):
        self.save_image(self.image, "original_image.png")

    def save_log_image(self):
        self.save_image(self.log_image, "log_image.png")

    def save_gamma_image(self):
        self.save_image(self.gamma_image, "gamma_image.png")

    def save_hist_image(self):
        self.save_image(self.hist_img, "histogram.png")


app = QApplication(sys.argv)
window = ImageProcessingApp()
window.showMaximized()
sys.exit(app.exec())
