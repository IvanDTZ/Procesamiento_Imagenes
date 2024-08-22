import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox, QMessageBox
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import cv2
import numpy as np
from colormath.color_objects import sRGBColor, CMYKColor
from colormath.color_conversions import convert_color
from PIL import Image


class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.converted_image = None
        self.current_format = 'RGB'
        self.setWindowTitle("Image Converter")
        self.setGeometry(100, 100, 1000, 600)

        self.layout = QVBoxLayout()

        self.load_button = QPushButton("Cargar Imagen")
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button)

        self.combo_box = QComboBox()
        self.combo_box.addItems(["RGB", "CMYK"])
        self.layout.addWidget(self.combo_box)

        self.convert_button = QPushButton("Convertir Imagen")
        self.convert_button.clicked.connect(self.convert_image)
        self.layout.addWidget(self.convert_button)

        self.save_button = QPushButton("Descargar Imagen Convertida")
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)

        self.image_layout = QHBoxLayout()
        self.original_image_label = QLabel("Imagen Original")
        self.converted_image_label = QLabel("Imagen Convertida")
        self.image_layout.addWidget(self.original_image_label)
        self.image_layout.addWidget(self.converted_image_label)
        self.layout.addLayout(self.image_layout)

        self.setLayout(self.layout)

    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")

        if file_path:
            self.image = cv2.imread(file_path)
            self.show_image(self.image, self.original_image_label)

    def show_image(self, image, label):
        qimage = self.convert_cv_qt(image)
        label.setPixmap(QPixmap.fromImage(qimage))

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return convert_to_Qt_format.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio)

    def convert_image(self):
        if self.image is None:
            QMessageBox.warning(
                self, "Error", "Primero debe cargar una imagen")
            return

        method = self.combo_box.currentText()

        if method == "RGB":
            converted_img = self.convert_to_rgb(self.image)
            self.current_format = 'RGB'
        elif method == "CMYK":
            converted_img = self.convert_to_cmyk(self.image)
            self.current_format = 'CMYK'

        self.converted_image = converted_img
        self.show_image(self.converted_image, self.converted_image_label)

    def convert_to_rgb(self, img):
        if img.shape[2] == 4:
            return self.cmyk_to_rgb(img)
        else:
            return img

    def convert_to_cmyk(self, img):
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb_img.shape
        cmyk_img = np.zeros((h, w, 4), dtype=np.uint8)

        for i in range(h):
            for j in range(w):
                rgb = sRGBColor(
                    rgb_img[i, j, 0] / 255.0, rgb_img[i, j, 1] / 255.0, rgb_img[i, j, 2] / 255.0)
                cmyk = convert_color(rgb, CMYKColor)
                cmyk_img[i, j, 0] = int(cmyk.get_value_tuple()[0] * 255)
                cmyk_img[i, j, 1] = int(cmyk.get_value_tuple()[1] * 255)
                cmyk_img[i, j, 2] = int(cmyk.get_value_tuple()[2] * 255)
                cmyk_img[i, j, 3] = int(cmyk.get_value_tuple()[3] * 255)

        return cmyk_img

    def cmyk_to_rgb(self, img):
        h, w, _ = img.shape
        rgb_img = np.zeros((h, w, 3), dtype=np.uint8)

        for i in range(h):
            for j in range(w):
                cmyk = CMYKColor(img[i, j, 0] / 255.0, img[i, j, 1] /
                                 255.0, img[i, j, 2] / 255.0, img[i, j, 3] / 255.0)
                rgb = convert_color(cmyk, sRGBColor)
                rgb_img[i, j, 0] = int(rgb.clamped_rgb_r * 255)
                rgb_img[i, j, 1] = int(rgb.clamped_rgb_g * 255)
                rgb_img[i, j, 2] = int(rgb.clamped_rgb_b * 255)

        return cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)

    def save_image(self):
        if self.converted_image is None:
            QMessageBox.warning(
                self, "Error", "No hay ninguna imagen convertida para descargar.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Guardar Imagen Convertida", "", "Images (*.png *.jpg *.jpeg *.bmp)")

        if file_path:

            pil_image = Image.fromarray(self.converted_image)
            pil_image.save(file_path)


def main():
    app = QApplication(sys.argv)
    window = ImageConverter()
    window.show()
    sys.exit(app.exec())


main()
