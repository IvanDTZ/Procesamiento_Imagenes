import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QScrollArea
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImageFilterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Filter Application')
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        self.imageLayout = QVBoxLayout()
        self.setupImageSection('Original', self.downloadOriginal)
        self.setupImageSection('High Pass Filter', self.downloadHighPass)
        self.setupImageSection('Low Pass Filter', self.downloadLowPass)
        self.setupImageSection('Band Pass Filter', self.downloadBandPass)
        self.setupImageSection('Band Stop Filter', self.downloadBandStop)

        loadButton = QPushButton('Cargar Imagen')
        loadButton.clicked.connect(self.loadAndApplyFilters)
        self.vbox.addWidget(loadButton)

        self.widget.setLayout(self.vbox)
        self.scroll.setWidget(self.widget)
        self.scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

    def setupImageSection(self, filter_name, download_function):
        layout = QHBoxLayout()
        label_title = QLabel(filter_name)
        label_image = QLabel('Imagen aquí')
        label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_download = QPushButton('Descargar ' + filter_name)
        button_download.clicked.connect(
            lambda: download_function(label_image.pixmap()))
        layout.addWidget(label_title)
        layout.addWidget(label_image)
        layout.addWidget(button_download)
        self.vbox.addLayout(layout)
        setattr(self, filter_name.replace(' ', '') + 'Label', label_image)

    def loadAndApplyFilters(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Abrir imagen', '/home', 'Image files (*.jpg *.png)')
        if fname:
            self.original_image = cv2.imread(fname)
            self.displayImage(self.original_image, self.OriginalLabel)
            self.applyAndDisplayFilters()

    def applyAndDisplayFilters(self):
        if self.original_image is not None:
            self.displayImage(self.applyHighPassFilter(),
                              self.HighPassFilterLabel)
            self.displayImage(self.applyLowPassFilter(),
                              self.LowPassFilterLabel)
            self.displayImage(self.applyBandPassFilter(),
                              self.BandPassFilterLabel)
            self.displayImage(self.applyBandStopFilter(),
                              self.BandStopFilterLabel)

    def applyHighPassFilter(self):
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        return cv2.filter2D(self.original_image, -1, kernel)

    def applyLowPassFilter(self):
        kernel = np.ones((5, 5), np.float32) / 25
        return cv2.filter2D(self.original_image, -1, kernel)

    def applyBandPassFilter(self):
        low = cv2.GaussianBlur(self.original_image, (17, 17), 0)
        return cv2.subtract(self.original_image, low)

    def applyBandStopFilter(self):
        low = cv2.GaussianBlur(self.original_image, (17, 17), 0)
        high = cv2.subtract(self.original_image, low)
        return cv2.add(self.original_image, high)

    def displayImage(self, img, label):
        qformat = QImage.Format.Format_Grayscale8 if len(
            img.shape) == 2 else QImage.Format.Format_RGB888
        outImage = QImage(
            img.data, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        label.setPixmap(QPixmap.fromImage(outImage).scaled(
            200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def downloadImage(self, pixmap, filter_name):
        if pixmap:
            fname, _ = QFileDialog.getSaveFileName(
                self, f'Guardar {filter_name}', '/home', 'Image files (*.jpg *.png)')
            if fname:
                pixmap.save(fname)

    def downloadOriginal(self, pixmap):
        self.downloadImage(pixmap, 'Original')

    def downloadHighPass(self, pixmap):
        self.downloadImage(pixmap, 'High Pass Filter')

    def downloadLowPass(self, pixmap):
        self.downloadImage(pixmap, 'Low Pass Filter')

    def downloadBandPass(self, pixmap):
        self.downloadImage(pixmap, 'Band Pass Filter')

    def downloadBandStop(self, pixmap):
        self.downloadImage(pixmap, 'Band Stop Filter')


app = QApplication(sys.argv)
ex = ImageFilterApp()
ex.show()
sys.exit(app.exec())
