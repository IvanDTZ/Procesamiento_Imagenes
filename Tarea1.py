import sys
import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Convertidor de Imágenes a Escala de Grises')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.btn_upload = QPushButton('Subir Imagen', self)
        self.btn_upload.clicked.connect(self.open_image)
        layout.addWidget(self.btn_upload)

        self.setLayout(layout)

    def open_image(self):
        options = QFileDialog.Option(0)
        options |= QFileDialog.Option.ReadOnly

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona una imagen", "", "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)

        if file_path:
            self.convert_to_grayscale(file_path)

    def convert_to_grayscale(self, file_path):
        try:

            image = cv2.imread(file_path)

            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            save_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar imagen en escala de grises", "", "Archivos PNG (*.png);;Archivos JPEG (*.jpg);;Archivos BMP (*.bmp)")

            if save_path:
                cv2.imwrite(save_path, grayscale_image)
                QMessageBox.information(
                    self, "Éxito", "Imagen guardada en escala de grises correctamente.")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo procesar la imagen: {e}")


def main():
    app = QApplication(sys.argv)
    ex = ImageConverter()
    ex.show()
    sys.exit(app.exec())


main()
