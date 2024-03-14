import cv2

class CameraController:

    def __init__(self, camera_number=0, width=1920, height=1080):
        self.camera_number = camera_number
        self.cap = None
        self.width = width
        self.height = height
        self.initialize_camera()

    def initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_number)
            if not self.cap.isOpened():
                raise Exception("Camera could not be initialized.")
            
            # Set the resolution to HD (1080p)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        except Exception as e:
            #print(f"Camera initialization error: {e}")
            exit()

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            #print("The image could not be captured")
            return None
        return cv2.flip(frame, 1)

    def release_camera(self):
        if self.cap:
            self.cap.release()
