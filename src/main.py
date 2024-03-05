import sys
import time
from PyQt5.QtWidgets import QApplication
import cv2
from controllers.camera_controller import CameraController
from controllers.face_controller import FaceController
from database.connection import Session
from utils.timer import Timer
from utils.ui_utils import draw_text
from views.main_window import MainWindow

def main():
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_()) 

if __name__ == "__main__":
    main()