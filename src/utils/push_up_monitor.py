import cv2
import math
import numpy as np
from utils.landmarks_detector import LandmarksDetector
from utils.ui_utils import draw_text
from utils.sound_effects import play_sound


class PushUpMonitor:
    def __init__(self):
        # self.counter
        self.count = 0
        self.direction = 0  # 0: Down, 1: Up
        self.form = 0
        self.feedback = "Colocate"
        # Started the Push up
        self.start = False

        self.detector = LandmarksDetector()

    def find_position(self, img, results, draw=True):
        self.landmarks_list = []
        
        for id, lm in enumerate(results.landmark):
            # Finding height, width of the image printed
            h, w, c = img.shape
            #Determining the pixels of the landmarks
            cx, cy = int(lm.x * w), int(lm.y * h)
            self.landmarks_list.append([id, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255,0,0), cv2.FILLED)
        return self.landmarks_list
    
    def find_angle(self, img, p1, p2, p3, draw=True):   
        #Get the landmarks
        x1, y1 = self.landmarks_list[p1][1:]
        x2, y2 = self.landmarks_list[p2][1:]
        x3, y3 = self.landmarks_list[p3][1:]
        
        # Calculate Angle
        angle = math.degrees(math.atan2(y3-y2, x3-x2) - 
                             math.atan2(y1-y2, x1-x2))
        if angle < 0:
            angle += 360
            if angle > 180:
                angle = 360 - angle
        elif angle > 180:
            angle = 360 - angle
        
        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255,255,255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255,255,255), 3)

            
            cv2.circle(img, (x1, y1), 5, (0,0,255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0,0,255), 2)
            cv2.circle(img, (x2, y2), 5, (0,0,255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0,0,255), 2)
            cv2.circle(img, (x3, y3), 5, (0,0,255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0,0,255), 2)
            
            cv2.putText(img, str(int(angle)), (x2-50, y2+50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)
        return angle

    def process(self, frame: np.array):
        frame_height, frame_width, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_landmarks = self.detector.detect_pushup_landmarks(image)

        # Bar position
        bar_width = 60  # Ancho de la barra
        bar_height = int(frame_height * 0.5)  # Altura de la barra, 50% de la altura del frame
        bar_x = 30  # Margen izquierdo de 10 píxeles
        bar_y = frame_height - bar_height - 30  # Margen inferior de 10 píxeles

        per = 0  # Initial percentage

        if pose_landmarks:

            self.detector.mp_drawing.draw_landmarks(
                frame, pose_landmarks, self.detector.mp_solutions.pose.POSE_CONNECTIONS)
        
            landmarks_list = self.find_position(frame, pose_landmarks, False)

            if len(landmarks_list) != 0:
                elbow = self.find_angle(frame, 11, 13, 15)
                shoulder = self.find_angle(frame, 13, 11, 23)
                hip = self.find_angle(frame, 11, 23,25)
                
                # Percentage of success of pushup
                per = np.interp(elbow, (90, 160), (0, 100))
                
                # Bar to show Pushup progress
                bar = np.interp(elbow, (90, 160), (380, 50))

                # Check to ensure right form before starting the program
                if elbow > 160 and shoulder > 40 and hip > 160:
                    self.form = 1
            
                # Check for full range of motion for the pushup
                if self.form == 1:
                    if per == 0:
                        if elbow <= 90 and hip > 160:
                            self.feedback = "Arriba"
                            if self.direction == 0:
                                self.count += 0.5
                                self.direction = 1
                                if self.count.is_integer():
                                    play_sound("counter")
                        else:
                            self.feedback = "Vuelve a tu posicion"
                            
                    if per == 100:
                        if elbow > 160 and shoulder > 40 and hip > 160:
                            self.feedback = "Abajo"
                            if self.direction == 1:
                                self.count += 0.5
                                self.direction = 0
                                if self.count.is_integer():
                                    play_sound("counter")
                        else:
                            self.feedback = "Vuelve a tu posicion"
                                # form = 0
        # Draw Bar
        if self.form == 1:
            cv2.rectangle(frame, (bar_x - 3, bar_y - 3), (bar_x + bar_width + 3, bar_y + bar_height + 3), (0, 0, 0), 2)  # Borde negro
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), cv2.FILLED)  # Fondo gris
            fill_height = int(bar_height * (per / 100))
            cv2.rectangle(frame, (bar_x, bar_y + bar_height - fill_height), (bar_x + bar_width, bar_y + bar_height), (0, 255, 0), cv2.FILLED)  # Barra verde
            cv2.putText(frame, f'{int(per)}%', (bar_x + 5, bar_y + bar_height - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)  # Texto negro
        
        # Display the Feedback
        frame_height, frame_width = frame.shape[0], frame.shape[1]
        text_width = cv2.getTextSize(self.feedback, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0][0]
        pos_msg_h = frame_height - 60
        pos_msg_w = (frame_width - text_width) // 2            
        draw_text(frame, self.feedback, pos=(pos_msg_w, pos_msg_h), font_scale=1, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))

        # Display the self.count
        draw_text(
                frame, 
                "CORRECTO: " + str(int(self.count)), 
                pos=(int(frame_width*0.90), 20),
                text_color=(255, 255, 230),
                font_scale=0.8,
                text_color_bg=(18, 185, 0)
        )

        return frame