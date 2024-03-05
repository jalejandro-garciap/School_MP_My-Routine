import time
import cv2
import numpy as np
from utils.ui_utils import draw_text, draw_dotted_line

class PushUpMonitor:
    
    def __init__(self, thresholds, flip_frame = False):        
        # Counters
        self.push_up_count  = 0
        self.push_up_count_bad  = 0
        #Set if frame should be flipped or not.
        self.flip_frame = flip_frame
        # Font type.
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # line type
        self.linetype = cv2.LINE_AA
        # set radius to draw arc
        self.radius = 20
        #  Activity time
        self.last_activity_time = time.time()

    def _update_push_up_counters_and_activity(self, angle_left, angle_right):
        if angle_left > self.thresholds['ARM_EXTENSION']['MIN'] and angle_right > self.thresholds['ARM_EXTENSION']['MIN']:
            self.push_up_count += 1
        else:
            self.push_up_count_bad += 1
        self.last_activity_time = time.time()

    def check_inactivity(self, frame):
        if time.time() - self.last_activity_time > self.thresholds['INACTIVE_THRESH']:
            self.push_up_count_good = 0
            self.push_up_count_bad = 0
            draw_text(frame, 'Resetting due to inactivity', (30, 100), self.font, 0.7, (0, 0, 255), 2, self.linetype)
        
    def calculate_angle(self, p1, p2, p3):
        ba = p1 - p2
        bc = p3 - p2
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def process(self, frame: np.array, pose):
        frame_width, _ = frame.shape
        
        # Process the image.
        keypoints = pose.process(frame)

        if keypoints:
            
            left_shoulder, left_elbow, left_wrist = keypoints['left_shoulder'], keypoints['left_elbow'], keypoints['left_wrist']
            right_shoulder, right_elbow, right_wrist = keypoints['right_shoulder'], keypoints['right_elbow'], keypoints['right_wrist']

            # Calculate the angle of the left and right arm
            angle_left = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            angle_right = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Update counters and uptime
            self.update_counters_and_activity(angle_left, angle_right)

            # Draw angles and dotted lines
            cv2.ellipse(frame, left_elbow, (30, 30), 0, 0, angle_left, (255, 255, 255), 2)  # Blanco para ángulo izquierdo
            cv2.ellipse(frame, right_elbow, (30, 30), 0, 0, angle_right, (255, 0, 0), 2)   # Azul para ángulo derecho
            draw_dotted_line(frame, left_elbow, left_shoulder, left_wrist, (255, 255, 255), 1)  # Líneas punteadas para visualización

            # Shows counters for good and bad push-ups
            draw_text(
                    frame, 
                    "CORRECT: " + str(self.push_up_count), 
                    pos=(int(frame_width*0.80), 20),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(18, 185, 0)
                ) 
            draw_text(
                    frame, 
                    "INCORRECT: " + str(self.push_up_count_bad), 
                    pos=(int(frame_width*0.80), 20),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(18, 185, 0)
                )

            # Check inactivity
            self.check_inactivity(frame)

            if self.flip_frame:
                frame = cv2.flip(frame, 1)

        else:
            self.check_inactivity(frame)

        return frame
