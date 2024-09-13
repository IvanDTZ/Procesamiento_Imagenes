import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor
from PyQt6.QtCore import Qt


class ImageGrid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            'Seleccionar un Píxel y Detectar Regiones Conectadas')
        self.image = None
        self.qimage = None
        self.grid_size = 10
        self.selected_pixel = None

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label = QLabel('Cargar una imagen para comenzar', self)

        self.load_button = QPushButton('Cargar Imagen', self)
        self.load_button.clicked.connect(self.load_image)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.load_button)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 'Seleccionar Imagen', '', 'Imagenes (*.png *.jpg *.bmp)')
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            self.display_image()

    def display_image(self):
        height, width = self.image.shape
        bytes_per_line = width
        self.qimage = QImage(self.image.data, width, height,
                             bytes_per_line, QImage.Format.Format_Grayscale8)

        pixmap = QPixmap.fromImage(self.qimage)
        self.image_label.setPixmap(pixmap)
        self.image_label.mousePressEvent = self.get_pixel_position
        self.draw_grid()

    def draw_grid(self):
        painter = QPainter(self.qimage)
        pen_color = QColor(0, 255, 0)
        painter.setPen(pen_color)

        height, width = self.image.shape
        for x in range(0, width, self.grid_size):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height, self.grid_size):
            painter.drawLine(0, y, width, y)

        pixmap = QPixmap.fromImage(self.qimage)
        self.image_label.setPixmap(pixmap)

    def get_pixel_position(self, event):
        if self.image is not None:
            x = event.position().x()
            y = event.position().y()

            grid_x = int(x // self.grid_size)
            grid_y = int(y // self.grid_size)

            self.selected_pixel = (
                grid_x * self.grid_size, grid_y * self.grid_size)

            height, width = self.image.shape
            if 0 <= self.selected_pixel[1] < height and 0 <= self.selected_pixel[0] < width:
                pixel_value = self.image[self.selected_pixel[1],
                                         self.selected_pixel[0]]
                self.info_label.setText(f'Seleccionaste el píxel en coordenadas {
                                        self.selected_pixel} con valor {pixel_value}')
                self.find_connected_regions()
            else:
                self.info_label.setText(f'Píxel fuera de los límites: {
                                        self.selected_pixel}')

    def find_connected_regions(self):
        if self.selected_pixel is not None:
            connected_image = np.zeros_like(self.image)
            connectivity = 8

            _, connected_image, _, _ = cv2.floodFill(self.image.copy(
            ), None, self.selected_pixel, 255, loDiff=10, upDiff=10, flags=connectivity)

            height, width = connected_image.shape
            bytes_per_line = width
            qimage_result = QImage(
                connected_image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)

            pixmap = QPixmap.fromImage(qimage_result)
            self.image_label.setPixmap(pixmap)


app = QApplication(sys.argv)
window = ImageGrid()
window.show()
sys.exit(app.exec())
