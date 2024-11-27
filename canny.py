# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 05:38:51 2024

@author: Eduardo
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QFileDialog, QLabel, QVBoxLayout, QPushButton, QWidget, QApplication
import sys


class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.setWindowTitle('Procesador de Imágenes con Filtro de Canny')
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout()

        # Etiquetas para mostrar la imagen original y la de bordes
        self.original_label = QLabel(self)
        self.bordes_label = QLabel(self)

        # Botón para seleccionar imagen
        self.select_button = QPushButton('Seleccionar Imagen')
        self.select_button.clicked.connect(self.select_image)

        # Agregar widgets al layout
        layout.addWidget(self.select_button)
        layout.addWidget(self.original_label)
        layout.addWidget(self.bordes_label)
        self.setLayout(layout)

    def select_image(self):
        # Diálogo para seleccionar imagen
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.bmp)")

        if file_path:
            self.apply_canny_filter(file_path)

    def apply_canny_filter(self, file_path):
        # Cargar y procesar la imagen
        imagen = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        bordes = cv2.Canny(imagen, 100, 200)

        # Convertir la imagen original y la de bordes para mostrar en PyQt
        original_image = QtGui.QImage(
            imagen.data, imagen.shape[1], imagen.shape[0], imagen.strides[0], QtGui.QImage.Format.Format_Grayscale8)
        bordes_image = QtGui.QImage(
            bordes.data, bordes.shape[1], bordes.shape[0], bordes.strides[0], QtGui.QImage.Format.Format_Grayscale8)

        # Mostrar las imágenes en las etiquetas
        self.original_label.setPixmap(
            QtGui.QPixmap.fromImage(original_image).scaled(400, 300))
        self.bordes_label.setPixmap(
            QtGui.QPixmap.fromImage(bordes_image).scaled(400, 300))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec())
