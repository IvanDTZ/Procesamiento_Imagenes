import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QPushButton
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


def convert_cv_to_qt(image):
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    q_image = QImage(image.data, width, height,
                     bytes_per_line, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(q_image)


class ImageComparisonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.original_label = QLabel(self)
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setText("Imagen Original")
        self.original_label.setScaledContents(True)

        self.corrected_label = QLabel(self)
        self.corrected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.corrected_label.setText("Imagen Corregida")
        self.corrected_label.setScaledContents(True)

        self.load_button = QPushButton("Cargar Imagen", self)
        self.load_button.clicked.connect(self.load_image)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.original_label)
        images_layout.addWidget(self.corrected_label)

        layout.addLayout(images_layout)
        self.setLayout(layout)
        self.setWindowTitle("Comparación de Imágenes")
        self.show()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        if file_name:
            image = cv2.imread(file_name)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                screen_width = self.width() // 2
                screen_height = self.height() // 2
                resized_image = cv2.resize(
                    image, (screen_width, screen_height))

                h, w = resized_image.shape[:2]
                focal_length = w
                center = (w / 2, h / 2)
                camera_matrix = np.array([[focal_length, 0, center[0]],
                                          [0, focal_length, center[1]],
                                          [0, 0, 1]])

                dist_coeffs = np.array([-0.3, 0.1, 0, 0, 0])
                undistorted_image = cv2.undistort(
                    resized_image, camera_matrix, dist_coeffs)

                original_pixmap = convert_cv_to_qt(resized_image)
                corrected_pixmap = convert_cv_to_qt(undistorted_image)

                self.original_label.setPixmap(original_pixmap)
                self.corrected_label.setPixmap(corrected_pixmap)

                self.original_label.resize(original_pixmap.size())
                self.corrected_label.resize(corrected_pixmap.size())


app = QApplication(sys.argv)
window = ImageComparisonWindow()
window.resize(1600, 900)
sys.exit(app.exec())
