import cv2
import numpy
import math

from models.body import Body
from utils.landmarks_detector import LandmarksDetector
class BodyController:

    AGE_LIST = ['0-2', '4-6', '8-12', '15-20', '25-32', '38-43', '48-53', '60-100']
    GENDER_LIST = ['Man', 'Woman']

    def __init__(self):  
        self.age_model = "src/data/models/age_deploy.prototxt"
        self.gender_model_path = "src/data/models/gender_deploy.prototxt"
        
        self.age_weights_path = "src/data/models/age_net.caffemodel"        
        self.gender_weights_path = "src/data/models/gender_net.caffemodel"

        self.age_net = cv2.dnn.readNet(self.age_model_path, self.age_weights_path)
        self.gender_net = cv2.dnn.readNet(self.gender_model_path, self.gender_weights_path)

        self.detector = LandmarksDetector()

    def euclidean_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def calculate_distance_between_eyes(eyes):
        if len(eyes) == 2:
            center_left_eye = (eyes[0][0] + eyes[0][2] // 2, eyes[0][1] + eyes[0][3] // 2)
            center_right_eye = (eyes[1][0] + eyes[1][2] // 2, eyes[1][1] + eyes[1][3] // 2)

            distance = numpy.sqrt((center_left_eye[0] - center_right_eye[0]) ** 2 +
                            (center_left_eye[1] - center_right_eye[1]) ** 2)

            return distance
        else:
            return None

    def detect_body(self, image):
        pose_landmarks = self.detector.get_pose_landmarks(image)

        if pose_landmarks:
            landmarks = pose_landmarks.landmark

            left_shoulder = [landmarks[self.detector.mp_pose.LEFT_SHOULDER.value].x,
                            landmarks[self.detector.mp_pose.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[self.detector.mp_pose.RIGHT_SHOULDER.value].x,
                            landmarks[self.detector.mp_pose.RIGHT_SHOULDER.value].y]
            left_hip = [landmarks[self.detector.mp_pose.LEFT_HIP.value].x,
                        landmarks[self.detector.mp_pose.LEFT_HIP.value].y]
            right_hip = [landmarks[self.detector.mp_pose.RIGHT_HIP.value].x,
                        landmarks[self.detector.mp_pose.RIGHT_HIP.value].y]

            shoulder_distance = self.euclidean_distance(*left_shoulder, *right_shoulder)
            waist_distance = self.euclidean_distance(*left_hip, *right_hip)

            if waist_distance == 0:
                return None, "Unable to calculate complexion due to detection issues."

            ratio = shoulder_distance / waist_distance
            return ratio
        else:
            return None, "No pose landmarks detected."
        
    def detect_hand_gesture(self, image):
        hand_landmarks = self.detector.detect_hand_landmarks(image)

        if hand_landmarks:
            landmarks = hand_landmarks.landmark

            index_tip = [landmarks[self.detector.mp_hands.INDEX_FINGER_TIP].x,
                        landmarks[self.detector.mp_hands.INDEX_FINGER_TIP].y]
            index_mcp = [landmarks[self.detector.mp_hands.INDEX_FINGER_MCP].x,
                        landmarks[self.detector.mp_hands.INDEX_FINGER_MCP].y]
            middle_mcp = [landmarks[self.detector.mp_hands.MIDDLE_FINGER_MCP].x,
                        landmarks[self.detector.mp_hands.MIDDLE_FINGER_MCP].y]
            ring_mcp = [landmarks[self.detector.mp_hands.RING_FINGER_MCP].x,
                        landmarks[self.detector.mp_hands.RING_FINGER_MCP].y]
            pinky_mcp = [landmarks[self.detector.mp_hands.PINKY_MCP].x,
                        landmarks[self.detector.mp_hands.PINKY_MCP].y]
            wrist =     [landmarks[self.detector.mp_hands.WRIST].x,
                        landmarks[self.detector.mp_hands.WRIST].y]

            if (index_tip[1] < index_mcp[1] and middle_mcp[1] < ring_mcp[1] < pinky_mcp[1]):
                if index_tip[0] < wrist[0]:
                    return "left"
                elif index_tip[0] > wrist[0]:
                    return "right"
        else:
            return None, "No hands landmarks detected."

    def analyze_body(self, frame, face, ratio):
        
        x, y, w, h = face.face
        face_blob = cv2.dnn.blobFromImage(frame[y:y+h, x:x+w], 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        
        self.gender_net.setInput(face_blob)
        gender_preds = self.gender_net.forward()
        gender = self.GENDER_LIST[gender_preds[0].argmax()]
        
        self.age_net.setInput(face_blob)
        age_preds = self.age_net.forward()
        age = self.AGE_LIST[age_preds[0].argmax()]

        distance_between_eyes = self.calculate_distance_between_eyes(face.eyes)
        if distance_between_eyes is not None:
            distance_in_cm = face.distance_between_eyes * 0.01 # Adjust this value based on the pixel-to-centimeter distance ratio.
            height = distance_in_cm * 1.5 # Adjust this value based on the relationship between distance in centimeters and height.
        else:
            height = None

        if ratio < 1.45:
            complexion = "Endomorph"
        elif ratio > 1.85:
            complexion = "Ectomorph"
        else:
            complexion = "Mesomorph"

        return Body(age=age, gender=gender, height=height, complexion=complexion)