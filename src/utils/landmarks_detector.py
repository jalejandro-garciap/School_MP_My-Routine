import cv2
import mediapipe

class LandmarksDetector:
    def __init__(self):
        # MediaPipe Solutions Initialization
        self.mp_solutions = mediapipe.solutions

        self.mp_facial = self.mp_solutions.face_mesh.FaceLandmark
        self.mp_pose = self.mp_solutions.pose.PoseLandmark
        self.mp_hands = self.mp_solutions.hands.HandLandmark

    def detect_facial_landmarks(self, image):
        with self.mp_solutions.face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return results.multi_face_landmarks

    def detect_hand_landmarks(self, image):
        with self.mp_solutions.hands.Hands(static_image_mode=True) as hands:
            results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return results.multi_hand_landmarks

    def detect_pose_landmarks(self, image):
        with self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return results.pose_landmarks