from PyQt5.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Rutina")
        self.setGeometry(100, 100, 600, 400)
        self.initUI()

    def initUI(self):
        self.label = QLabel("Bienvenido a Mi Rutina", self)
        self.label.move(200, 200)