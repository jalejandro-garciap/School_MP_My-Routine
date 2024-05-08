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

    def find_available_camera(self):
        max_attempts = 10  # Set the expected range of camera ratings
        for i in range(max_attempts):
            if i == self.camera_number:
                continue  # # Skip current camera
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                test_cap.release()
                return i
        return None

    def change_camera(self, new_camera_number=None):
        if new_camera_number is None:
            new_camera_number = self.find_available_camera()
            if new_camera_number is not None:
                self.camera_number = new_camera_number
                self.initialize_camera()
                print(f"Switched to camera {new_camera_number}.")
            else:
                print("No new cameras found. Keeping the current camera.")
        else:
          if new_camera_number != self.camera_number:
            self.camera_number = new_camera_number
            self.initialize_camera()