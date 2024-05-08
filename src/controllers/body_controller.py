import statistics
import cv2
import numpy
import math
import threading

from models.body import Body
from utils.landmarks_detector import LandmarksDetector
class BodyController:

    AGE_LIST = ['0-2', '4-6', '8-12', '15-20', '25-32', '38-43', '48-53', '60-100']
    GENDER_LIST = ['Man', 'Woman']

    def __init__(self):  
        self.age_model_path = "src/data/models/age_deploy.prototxt"
        self.gender_model_path = "src/data/models/gender_deploy.prototxt"
        
        self.age_weights_path = "src/data/models/age_net.caffemodel"        
        self.gender_weights_path = "src/data/models/gender_net.caffemodel"

        self.age_net = cv2.dnn.readNet(self.age_model_path, self.age_weights_path)
        self.gender_net = cv2.dnn.readNet(self.gender_model_path, self.gender_weights_path)

        self.detector = LandmarksDetector()
        self.body = Body()

        self.bodies = []

        self.captured_body = False
        self.analysis_started = False
        self.analysis_finished = False        

    def get_mode(self, array):
        try:
            return statistics.mode(array)
        except statistics.StatisticsError:
            return None

    def euclidean_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def calculate_distance_between_eyes(self, eyes):
        if len(eyes) == 2:
            center_left_eye = (eyes[0][0] + eyes[0][2] // 2, eyes[0][1] + eyes[0][3] // 2)
            center_right_eye = (eyes[1][0] + eyes[1][2] // 2, eyes[1][1] + eyes[1][3] // 2)

            distance = numpy.sqrt((center_left_eye[0] - center_right_eye[0]) ** 2 +
                            (center_left_eye[1] - center_right_eye[1]) ** 2)

            return distance
        else:
            return None

    def detect_body(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_landmarks = self.detector.detect_pose_landmarks(image)

        if pose_landmarks:
            landmarks = pose_landmarks.landmark
            self.detector.mp_drawing.draw_landmarks(
                frame, pose_landmarks, self.detector.mp_solutions.pose.POSE_CONNECTIONS)

            try:
                left_shoulder = [landmarks[self.detector.mp_pose.LEFT_SHOULDER.value].x,
                                landmarks[self.detector.mp_pose.LEFT_SHOULDER.value].y]
                right_shoulder = [landmarks[self.detector.mp_pose.RIGHT_SHOULDER.value].x,
                                landmarks[self.detector.mp_pose.RIGHT_SHOULDER.value].y]
                left_hip = [landmarks[self.detector.mp_pose.LEFT_HIP.value].x,
                            landmarks[self.detector.mp_pose.LEFT_HIP.value].y]
                right_hip = [landmarks[self.detector.mp_pose.RIGHT_HIP.value].x,
                            landmarks[self.detector.mp_pose.RIGHT_HIP.value].y]
            except IndexError:
                #print("Unable to calculate dimensions due to detection issues.")
                return None

            shoulder_distance = self.euclidean_distance(*left_shoulder, *right_shoulder)
            waist_distance = self.euclidean_distance(*left_hip, *right_hip)

            if waist_distance == 0:
                #print("Unable to calculate complexion due to detection issues.")
                return None

            ratio = shoulder_distance / waist_distance
            return ratio
        else:
            #print("No pose landmarks detected.")
            return None
        
    def detect_arm_raised(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_landmarks = self.detector.detect_pose_landmarks(image)

        if pose_landmarks:
            landmarks = pose_landmarks.landmark
            try:
                left_shoulder = landmarks[self.detector.mp_pose.LEFT_SHOULDER.value]
                right_shoulder = landmarks[self.detector.mp_pose.RIGHT_SHOULDER.value]
                left_elbow = landmarks[self.detector.mp_pose.LEFT_ELBOW.value]
                right_elbow = landmarks[self.detector.mp_pose.RIGHT_ELBOW.value]

                # Determine if it is the left or right arm
                if left_elbow.y < left_shoulder.y:
                    return "right" # To analize
                if right_elbow.y < right_shoulder.y:
                    return "left" # To analize

            except IndexError:
                #print("Incomplete hand landmarks detected.")
                return None
        else:
            #print("No pose landmarks detected.")
            return None

    def analyze_body(self, frame, faces):
        self.analysis_started = True
        analysis_thread = threading.Thread(target=self.analyze_body_async, args=(frame, faces))
        analysis_thread.start()        
    
    def analyze_body_async(self, frame, faces):

        ages, genders, heights, complexions = [], [], [], []

        for face in faces:
            x, y, w, h = face.face[0]
            face_blob = cv2.dnn.blobFromImage(frame[y:y+h, x:x+w], 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        
            self.gender_net.setInput(face_blob)
            gender_preds = self.gender_net.forward()
            genders.append(self.GENDER_LIST[gender_preds[0].argmax()])
            
            self.age_net.setInput(face_blob)
            age_preds = self.age_net.forward()
            ages.append(self.AGE_LIST[age_preds[0].argmax()])
            
            distance_between_eyes = self.calculate_distance_between_eyes(face.eyes)
            if distance_between_eyes is not None:
                distance_in_cm = distance_between_eyes * 0.01 # Adjust this value based on the pixel-to-centimeter distance ratio.
                heights.append(distance_in_cm * 1.5) # Adjust this value based on the relationship between distance in centimeters and height.

        for ratio in self.bodies:
            if ratio < 1.45:
                complexions.append("Endomorph")
            elif ratio > 1.85:
                complexions.append("Ectomorph")
            else:
                complexions.append("Mesomorph")

        self.body = Body(
            age = self.get_mode(ages),
            gender = self.get_mode(genders),
            height = self.get_mode(heights),
            complexion = self.get_mode(complexions)
        )

        self.analysis_finished = True