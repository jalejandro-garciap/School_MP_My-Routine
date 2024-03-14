import cv2
import numpy as np
from utils.landmarks_detector import LandmarksDetector
from utils.ui_utils import draw_text

class PushUpMonitor:
    def __init__(self):
        # Counter
        self.count = 0
        # Started the Push up
        self.start = False

        self.detector = LandmarksDetector()

    def calculate_distance(self, p1, p2):
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    def process(self, frame: np.array):
        frame_height, frame_width, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_height, image_width, _ = image.shape
        pose_landmarks = self.detector.detect_pose_landmarks(image)        

        if pose_landmarks:
            ps_lm = pose_landmarks.landmark

            nose = (int(ps_lm[0].x*image_width), int(ps_lm[0].y*image_height))
            left_wrist = (int(ps_lm[15].x*image_width), int(ps_lm[15].y*image_height))
            right_wrist = (int(ps_lm[16].x*image_width), int(ps_lm[16].y*image_height))
            left_shoulder = (int(ps_lm[11].x*image_width), int(ps_lm[11].y*image_height))
            right_shoulder = (int(ps_lm[12].x*image_width), int(ps_lm[12].y*image_height))
            left_hip = (int(ps_lm[23].x*image_width), int(ps_lm[23].y*image_height)) 
            right_hip = (int(ps_lm[24].x*image_width), int(ps_lm[24].y*image_height))
            left_heel = (int(ps_lm[29].x*image_width), int(ps_lm[29].y*image_height))
            right_heel = (int(ps_lm[30].x*image_width), int(ps_lm[30].y*image_height))

            # Draw ing body parts on the image

            cv2.circle(frame, nose, 8, (255, 0, 0), -1)
            cv2.circle(frame, left_wrist, 8, (225, 105, 65), -1)
            cv2.circle(frame, right_wrist, 8, (250, 206, 135), -1)
            cv2.circle(frame, left_shoulder, 8, (230, 250, 0), -1)
            cv2.circle(frame, right_shoulder, 8, (212, 250, 127), -1)
            cv2.circle(frame, left_hip, 8, (0, 128, 0), -1)
            cv2.circle(frame, right_hip, 8, (144, 238, 144), -1)
            cv2.circle(frame, left_heel, 8, (0, 255, 255), -1)
            cv2.circle(frame, right_heel, 8, (224, 255, 255), -1)

            midpoint = ((left_shoulder[0] + right_shoulder[0]) // 2, (left_shoulder[1] + right_shoulder[1]) // 2)

            cv2.line(frame, nose, midpoint, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, left_shoulder, right_shoulder, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, left_shoulder, left_wrist, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, right_shoulder, right_wrist, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, left_shoulder, left_hip, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, right_shoulder, right_hip, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, right_hip, left_hip, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, left_hip, left_heel, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.line(frame, right_hip, right_heel, (255, 255, 255), 4, cv2.LINE_AA)

            # Validate push up

            if self.calculate_distance(right_shoulder,right_wrist) < 60: 
                self.start = True
            elif self.start and self.calculate_distance(right_shoulder,right_wrist) > 90:
                self.count += 1
                self.start = False
    
        # Display the count
        draw_text(
                frame, 
                "CORRECTO: " + str(self.count), 
                pos=(int(frame_width*0.90), 20),
                text_color=(255, 255, 230),
                font_scale=0.8,
                text_color_bg=(18, 185, 0)
        )

        return frame