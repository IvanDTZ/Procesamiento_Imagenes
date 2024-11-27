import sys
import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QPushButton, QWidget, QSlider, QHBoxLayout, QComboBox

# Clase principal de la aplicación de detección de objetos


class ObjectDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Sistema de Detección y Modificación Inteligente de Objetos")
        self.setGeometry(100, 100, 1000, 800)

        # Captura de video con OpenCV
        self.cap = cv2.VideoCapture(0)

        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layouts
        self.layout = QVBoxLayout()
        self.control_layout = QHBoxLayout()

        self.video_label = QLabel(self)
        # Tamaño fijo para el feed de video
        self.video_label.setFixedSize(640, 480)
        self.layout.addWidget(self.video_label)

        # Botones para detección y filtros
        self.haar_button = QPushButton("Detectar Rostros", self)
        self.haar_button.clicked.connect(self.toggle_haar_detection)
        self.control_layout.addWidget(self.haar_button)

        self.segment_color_button = QPushButton("Segmentar por Color", self)
        self.segment_color_button.clicked.connect(
            self.toggle_color_segmentation)
        self.control_layout.addWidget(self.segment_color_button)

        # Combo box para selección de filtros
        self.filter_selector = QComboBox(self)
        self.filter_selector.addItems(["Sin filtro", "Desenfoque Gaussiano",
                                      "Detección de Bordes (Sobel)", "Detección de Bordes (Laplaciano)"])
        self.filter_selector.currentIndexChanged.connect(self.set_filter)
        self.control_layout.addWidget(self.filter_selector)

        # Sliders para tonalidad y brillo
        self.hue_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(179)
        self.hue_slider.setValue(90)
        self.hue_slider.setToolTip("Cambiar tonalidad")
        self.hue_slider.valueChanged.connect(self.update_hue)
        self.control_layout.addWidget(QLabel("Tonalidad:"))
        self.control_layout.addWidget(self.hue_slider)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setToolTip("Cambiar brillo")
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        self.control_layout.addWidget(QLabel("Brillo:"))
        self.control_layout.addWidget(self.brightness_slider)

        self.layout.addLayout(self.control_layout)
        self.central_widget.setLayout(self.layout)

        # Variables
        self.apply_haar = False
        self.apply_color_segmentation = False
        self.hue_value = 90
        self.brightness_value = 0
        self.active_filter = None  # Filtro actual
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Temporizador para el feed de video
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    # Método para activar/desactivar la detección de rostros
    def toggle_haar_detection(self):
        self.apply_haar = not self.apply_haar
        if self.apply_haar:
            self.haar_button.setText("Desactivar Rostros")
        else:
            self.haar_button.setText("Detectar Rostros")

    # Método para activar/desactivar la segmentación por color
    def toggle_color_segmentation(self):
        self.apply_color_segmentation = not self.apply_color_segmentation
        if self.apply_color_segmentation:
            self.segment_color_button.setText(
                "Desactivar Segmentación por Color")
        else:
            self.segment_color_button.setText("Segmentar por Color")

    # Método para establecer el filtro activo
    def set_filter(self, index):
        filters = [None, "gaussian_blur", "sobel", "laplacian"]
        self.active_filter = filters[index]

    # Método para actualizar el valor de la tonalidad
    def update_hue(self, value):
        self.hue_value = value

    # Método para actualizar el valor del brillo
    def update_brightness(self, value):
        self.brightness_value = value

    # Método para aplicar el filtro seleccionado
    def apply_filter(self, frame):
        if self.active_filter == "gaussian_blur":
            return cv2.GaussianBlur(frame, (15, 15), 0)
        elif self.active_filter == "sobel":
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel = cv2.magnitude(sobelx, sobely)
            return cv2.cvtColor(np.uint8(sobel), cv2.COLOR_GRAY2RGB)
        elif self.active_filter == "laplacian":
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            return cv2.cvtColor(np.uint8(np.absolute(laplacian)), cv2.COLOR_GRAY2RGB)
        return frame

    # Método para aplicar modificaciones HSV (tonalidad y brillo)
    def apply_hsv_modifications(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        hue, sat, val = cv2.split(hsv)
        hue[:] = self.hue_value
        val = cv2.add(val, self.brightness_value)
        modified_hsv = cv2.merge([hue, sat, val])
        return cv2.cvtColor(modified_hsv, cv2.COLOR_HSV2RGB)

    # Método para segmentar por color
    def segment_color(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        segmented = cv2.bitwise_and(frame, frame, mask=mask)
        return segmented

    # Método para actualizar el frame del video
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Aplicar detección de rostros con Haar Cascade
        if self.apply_haar:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            faces = self.haar_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Aplicar segmentación por color
        if self.apply_color_segmentation:
            frame = self.segment_color(frame)

        # Aplicar modificaciones HSV (tonalidad y brillo)
        frame = self.apply_hsv_modifications(frame)

        # Aplicar filtro seleccionado
        frame = self.apply_filter(frame)

        # Redimensionar frame para ajustarlo al QLabel
        label_width = self.video_label.width()
        label_height = self.video_label.height()
        frame = cv2.resize(frame, (label_width, label_height),
                           interpolation=cv2.INTER_AREA)

        # Mostrar frame
        height, width, channel = frame.shape
        step = channel * width
        q_image = QImage(frame.data, width, height, step,
                         QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    # Método para liberar la captura de video al cerrar la aplicación
    def closeEvent(self, event):
        self.cap.release()


# Código principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ObjectDetectionApp()
    window.show()
    sys.exit(app.exec())
