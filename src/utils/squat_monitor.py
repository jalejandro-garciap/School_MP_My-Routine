import time
import cv2
import numpy as np
from utils.ui_utils import draw_text, draw_dotted_line

class SquatMonitor:
    
    # Colors in BGR format.
    COLORS = {
        'blue'       : (0, 127, 255),
        'red'        : (255, 50, 50),
        'green'      : (0, 255, 127),
        'light_green': (100, 233, 127),
        'yellow'     : (255, 255, 0),
        'magenta'    : (255, 0, 255),
        'white'      : (255,255,255),
        'cyan'       : (0, 255, 255),
        'light_blue' : (102, 204, 255)
    }

    FEEDBACK_ID_MAP = {
        0: ('BEND BACKWARDS', 215, (0, 153, 255)),
        1: ('BEND FORWARD', 215, (0, 153, 255)),
        2: ('KNEE FALLING OVER TOE', 170, (255, 80, 80)),
        3: ('SQUAT TOO DEEP', 125, (255, 80, 80))
    }

    def __init__(self, thresholds, flip_frame = False):        
        # Counter
        self.squat_count = 0
        #Set if frame should be flipped or not.
        self.flip_frame = flip_frame
        # self.thresholds
        self.thresholds = thresholds
        # Font type.
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        # line type
        self.linetype = cv2.LINE_AA
        # set radius to draw arc
        self.radius = 20

        # Dictionary to maintain the various landmark features.
        
        self.left_features = {
            'shoulder': 11,
            'elbow'   : 13,
            'wrist'   : 15,                    
            'hip'     : 23,
            'knee'    : 25,
            'ankle'   : 27,
            'foot'    : 31
        }

        self.right_features = {
            'shoulder': 12,
            'elbow'   : 14,
            'wrist'   : 16,
            'hip'     : 24,
            'knee'    : 26,
            'ankle'   : 28,
            'foot'    : 32
        }
        
        self.dict_features = {}
        self.dict_features['left'] = self.left_features
        self.dict_features['right'] = self.right_features
        self.dict_features['nose'] = 0

        
        # For tracking counters and sharing states in and out of callbacks.
        self.state_tracker = {
            'state_seq': [],

            'SQUAT_COUNT': 0,
            'IMPROPER_SQUAT':0,

            'LOWER_HIPS': False,
            'INCORRECT_POSTURE': False,

            'start_inactive_time': time.perf_counter(),
            'start_inactive_time_front': time.perf_counter(),
            'INACTIVE_TIME': 0.0,
            'INACTIVE_TIME_FRONT': 0.0,

            # 0 --> Bend Backwards, 1 --> Bend Forward, 2 --> Keep shin straight, 3 --> Deep squat
            'DISPLAY_TEXT' : np.full((4,), False),
            'COUNT_FRAMES' : np.zeros((4,), dtype=np.int64),           

            'prev_state': None,
            'curr_state':None            
        }

    def _get_state(self, knee_angle):
        states = [(self.thresholds['HIP_KNEE_VERT']['NORMAL'], 1),
                  (self.thresholds['HIP_KNEE_VERT']['TRANS'], 2),
                  (self.thresholds['HIP_KNEE_VERT']['PASS'], 3)]
        
        for (min_val, max_val), state in states:
            if min_val <= knee_angle <= max_val:
                return f's{state}'
        return None
    
    def _update_state_sequence(self, state):
        valid_transitions = {'s2': ['s3'], 's3': ['s2']}

        # Check if transition from current state is valid
        if state in valid_transitions and not any(s in self.state_tracker['state_seq'] for s in valid_transitions[state]):
            self.state_tracker['state_seq'].append(state)

        # Directly append 's3' if 's2' is already in the sequence
        elif state == 's3' and 's2' in self.state_tracker['state_seq']:
            self.state_tracker['state_seq'].append(state)

    def _update_squat_counters(self):
        if len(self.state_tracker['state_seq']) == 3 and not self.state_tracker['INCORRECT_POSTURE']:
            self.state_tracker['SQUAT_COUNT'] += 1
            self.squat_count += 1
            return str(self.state_tracker['SQUAT_COUNT'])
        elif 's2' in self.state_tracker['state_seq'] and len(self.state_tracker['state_seq']) == 1 or self.state_tracker['INCORRECT_POSTURE']:
            self.state_tracker['IMPROPER_SQUAT'] += 1
            return 'incorrect'
        self.state_tracker['state_seq'] = []
        self.state_tracker['INCORRECT_POSTURE'] = False
        return None
    
    def _update_inactivity(self):
        end_time = time.perf_counter()
        inactivity_period = end_time - self.state_tracker['start_inactive_time']
        self.state_tracker['INACTIVE_TIME'] += inactivity_period
        self.state_tracker['start_inactive_time'] = end_time

        if self.state_tracker['INACTIVE_TIME'] >= self.thresholds['INACTIVE_THRESH']:
            self.state_tracker['SQUAT_COUNT'] = 0
            self.state_tracker['IMPROPER_SQUAT'] = 0
            return True  
        return False  

    def _show_feedback(self, frame, c_frame, dict_maps, lower_hips_disp):
        if lower_hips_disp:
            draw_text(frame, 'LOWER YOUR HIPS', pos=(30, 80), text_color=(0, 0, 0), font_scale=0.6, text_color_bg=(255, 255, 0))  

        for idx in np.where(c_frame)[0]:
            draw_text(frame, dict_maps[idx][0], pos=(30, dict_maps[idx][1]), text_color=(255, 255, 230), font_scale=0.6, text_color_bg=dict_maps[idx][2])

        return frame

    def _get_landmark_array(pose_landmark, key, frame_width, frame_height):
        denorm_x = int(pose_landmark[key].x * frame_width)
        denorm_y = int(pose_landmark[key].y * frame_height)
        return np.array([denorm_x, denorm_y])

    def _get_landmark_features(self, kp_results, dict_features, feature, frame_width, frame_height):
        if feature == 'nose':
            return self.get_landmark_array(kp_results, dict_features[feature], frame_width, frame_height)

        elif feature == 'left' or 'right':
            shldr_coord = self.get_landmark_array(kp_results, dict_features[feature]['shoulder'], frame_width, frame_height)
            elbow_coord = self.get_landmark_array(kp_results, dict_features[feature]['elbow'], frame_width, frame_height)
            wrist_coord = self.get_landmark_array(kp_results, dict_features[feature]['wrist'], frame_width, frame_height)
            hip_coord   = self.get_landmark_array(kp_results, dict_features[feature]['hip'], frame_width, frame_height)
            knee_coord  = self.get_landmark_array(kp_results, dict_features[feature]['knee'], frame_width, frame_height)
            ankle_coord = self.get_landmark_array(kp_results, dict_features[feature]['ankle'], frame_width, frame_height)
            foot_coord  = self.get_landmark_array(kp_results, dict_features[feature]['foot'], frame_width, frame_height)

            return shldr_coord, elbow_coord, wrist_coord, hip_coord, knee_coord, ankle_coord, foot_coord
        else:
            raise ValueError("feature needs to be either 'nose', 'left' or 'right")

    def find_angle(p1, p2, ref_pt = np.array([0,0])):
        p1_ref = p1 - ref_pt
        p2_ref = p2 - ref_pt
        cos_theta = (np.dot(p1_ref,p2_ref)) / (1.0 * np.linalg.norm(p1_ref) * np.linalg.norm(p2_ref))
        theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))                
        degree = int(180 / np.pi) * theta
        return int(degree)

    def perform_feedback_actions(self, hip_vertical_angle, knee_vertical_angle, ankle_vertical_angle):
        if hip_vertical_angle > self.thresholds['HIP_THRESH'][1]:
            self.state_tracker['DISPLAY_TEXT'][0] = True
        elif hip_vertical_angle < self.thresholds['HIP_THRESH'][0] and self.state_tracker['state_seq'].count('s2') == 1:
            self.state_tracker['DISPLAY_TEXT'][1] = True

        if self.thresholds['KNEE_THRESH'][0] < knee_vertical_angle < self.thresholds['KNEE_THRESH'][1] and self.state_tracker['state_seq'].count('s2') == 1:
            self.state_tracker['LOWER_HIPS'] = True
        elif knee_vertical_angle > self.thresholds['KNEE_THRESH'][2]:
            self.state_tracker['DISPLAY_TEXT'][3] = True
            self.state_tracker['INCORRECT_POSTURE'] = True

        if ankle_vertical_angle > self.thresholds['ANKLE_THRESH']:
            self.state_tracker['DISPLAY_TEXT'][2] = True
            self.state_tracker['INCORRECT_POSTURE'] = True

    def process(self, frame: np.array, pose):
        play_sound = None
        frame_height, frame_width, _ = frame.shape

        # Process the image.
        keypoints = pose.process(frame)

        if keypoints.pose_landmarks:
            ps_lm = keypoints.pose_landmarks

            nose_coord = self._get_landmark_features(ps_lm.landmark, self.dict_features, 'nose', frame_width, frame_height)
            left_coords = self._get_landmark_features(ps_lm.landmark, self.dict_features, 'left', frame_width, frame_height)
            right_coords = self._get_landmark_features(ps_lm.landmark, self.dict_features, 'right', frame_width, frame_height)

            (left_shldr_coord, left_elbow_coord, left_wrist_coord, 
            left_hip_coord, left_knee_coord, left_ankle_coord, left_foot_coord) = left_coords

            (right_shldr_coord, right_elbow_coord, right_wrist_coord, 
            right_hip_coord, right_knee_coord, right_ankle_coord, right_foot_coord) = right_coords

            offset_angle = self.find_angle(left_shldr_coord, right_shldr_coord, nose_coord)

            if offset_angle > self.thresholds['OFFSET_THRESH']:
                
                display_inactivity = False

                end_time = time.perf_counter()
                self.state_tracker['INACTIVE_TIME_FRONT'] += end_time - self.state_tracker['start_inactive_time_front']
                self.state_tracker['start_inactive_time_front'] = end_time

                if self.state_tracker['INACTIVE_TIME_FRONT'] >= self.thresholds['INACTIVE_THRESH']:
                    self.state_tracker['SQUAT_COUNT'] = 0
                    self.state_tracker['IMPROPER_SQUAT'] = 0
                    display_inactivity = True

                cv2.circle(frame, nose_coord, 7, self.COLORS['white'], -1)
                cv2.circle(frame, left_shldr_coord, 7, self.COLORS['yellow'], -1)
                cv2.circle(frame, right_shldr_coord, 7, self.COLORS['magenta'], -1)

                if self.flip_frame:
                    frame = cv2.flip(frame, 1)

                if display_inactivity:
                    cv2.putText(frame, 'Resetting SQUAT_COUNT due to inactivity!!!', (10, frame_height - 90), 
                    self.font, 0.5, self.COLORS['blue'], 2, lineType=self.linetype)
                    play_sound = 'reset_counters'
                    self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
                    self.state_tracker['start_inactive_time_front'] = time.perf_counter()

                draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['SQUAT_COUNT']), 
                    pos=(int(frame_width*0.80), 20),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(18, 185, 0)
                )  
                draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_SQUAT']), 
                    pos=(int(frame_width*0.80), 60),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(221, 0, 0),
                )  
                
                draw_text(
                    frame, 
                    'CAMERA NOT ALIGNED CORRECTLY!!!', 
                    pos=(30, frame_height-60),
                    text_color=(255, 255, 230),
                    font_scale=0.50,
                    text_color_bg=(255, 153, 0),
                ) 
                
                draw_text(
                    frame, 
                    'ANGLE COMPENSATED: '+str(offset_angle), 
                    pos=(30, frame_height-30),
                    text_color=(255, 255, 230),
                    font_scale=0.50,
                    text_color_bg=(255, 153, 0),
                ) 

                # Reset inactive times for side view.
                self.state_tracker['start_inactive_time'] = time.perf_counter()
                self.state_tracker['INACTIVE_TIME'] = 0.0
                self.state_tracker['prev_state'] =  None
                self.state_tracker['curr_state'] = None
            
            # Camera is aligned properly.
            
            else:

                self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
                self.state_tracker['start_inactive_time_front'] = time.perf_counter()

                dist_l_sh_hip = abs(left_foot_coord[1] - left_shldr_coord[1])
                dist_r_sh_hip = abs(right_foot_coord[1] - right_shldr_coord[1])

                coords_by_side = {
                    'left': (left_shldr_coord, left_elbow_coord, left_wrist_coord, left_hip_coord, left_knee_coord, left_ankle_coord, left_foot_coord),
                    'right': (right_shldr_coord, right_elbow_coord, right_wrist_coord, right_hip_coord, right_knee_coord, right_ankle_coord, right_foot_coord)
                }
                
                side = 'left' if dist_l_sh_hip > dist_r_sh_hip else 'right'
                (shldr_coord, elbow_coord, wrist_coord, hip_coord, knee_coord, ankle_coord, foot_coord) = coords_by_side[side]
                
                multiplier = -1 if side == 'left' else 1

                # Vertical angle calculation
                
                hip_vertical_angle = self.find_angle(shldr_coord, np.array([hip_coord[0], 0]), hip_coord)
                cv2.ellipse(frame, hip_coord, (30, 30), 
                            angle = 0, startAngle = -90, endAngle = -90+multiplier*hip_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3, lineType = self.linetype)

                draw_dotted_line(frame, hip_coord, start=hip_coord[1]-80, end=hip_coord[1]+20, line_color=self.COLORS['blue'])

                knee_vertical_angle = self.find_angle(hip_coord, np.array([knee_coord[0], 0]), knee_coord)
                cv2.ellipse(frame, knee_coord, (20, 20), 
                            angle = 0, startAngle = -90, endAngle = -90-multiplier*knee_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3,  lineType = self.linetype)

                draw_dotted_line(frame, knee_coord, start=knee_coord[1]-50, end=knee_coord[1]+20, line_color=self.COLORS['blue'])

                ankle_vertical_angle = self.find_angle(knee_coord, np.array([ankle_coord[0], 0]), ankle_coord)
                cv2.ellipse(frame, ankle_coord, (30, 30),
                            angle = 0, startAngle = -90, endAngle = -90 + multiplier*ankle_vertical_angle,
                            color = self.COLORS['white'], thickness = 3,  lineType=self.linetype)

                draw_dotted_line(frame, ankle_coord, start=ankle_coord[1]-50, end=ankle_coord[1]+20, line_color=self.COLORS['blue'])
                        
                # Join landmarks.
                cv2.line(frame, shldr_coord, elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, wrist_coord, elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, shldr_coord, hip_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, knee_coord, hip_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, ankle_coord, knee_coord,self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, ankle_coord, foot_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                
                # Plot landmark points
                cv2.circle(frame, shldr_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, elbow_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, wrist_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, hip_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, knee_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, ankle_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, foot_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)

                current_state = self._get_state(int(knee_vertical_angle))
                self.state_tracker['curr_state'] = current_state
                self._update_state_sequence(current_state)

                # Compute counters

                if current_state == 's1':
                    play_sound = self._update_squat_counters(self)
                else:
                    self.perform_feedback_actions(self, hip_vertical_angle, knee_vertical_angle, ankle_vertical_angle)
                
                # Compute inactivity

                if self.state_tracker['curr_state'] == self.state_tracker['prev_state']:
                    display_inactivity = self._update_inactivity(self)
                else:
                    self.state_tracker['start_inactive_time'] = time.perf_counter()
                    self.state_tracker['INACTIVE_TIME'] = 0.0

                hip_text_coord_x = hip_coord[0] + 10
                knee_text_coord_x = knee_coord[0] + 15
                ankle_text_coord_x = ankle_coord[0] + 10

                if self.flip_frame:
                    frame = cv2.flip(frame, 1)
                    hip_text_coord_x = frame_width - hip_coord[0] + 10
                    knee_text_coord_x = frame_width - knee_coord[0] + 15
                    ankle_text_coord_x = frame_width - ankle_coord[0] + 10
                
                if 's3' in self.state_tracker['state_seq'] or current_state == 's1':
                    self.state_tracker['LOWER_HIPS'] = False

                self.state_tracker['COUNT_FRAMES'][self.state_tracker['DISPLAY_TEXT']]+=1

                frame = self._show_feedback(frame, self.state_tracker['COUNT_FRAMES'], self.FEEDBACK_ID_MAP, self.state_tracker['LOWER_HIPS'])

                if display_inactivity:
                    cv2.putText(frame, 'Resetting COUNTERS due to inactivity!!!', (10, frame_height - 20), self.font, 0.5, self.COLORS['blue'], 2, lineType=self.linetype)
                    play_sound = 'reset_counters'
                    self.state_tracker['start_inactive_time'] = time.perf_counter()
                    self.state_tracker['INACTIVE_TIME'] = 0.0
                
                cv2.putText(frame, str(int(hip_vertical_angle)), (hip_text_coord_x, hip_coord[1]), self.font, 0.6, self.COLORS['light_green'], 2, lineType=self.linetype)
                cv2.putText(frame, str(int(knee_vertical_angle)), (knee_text_coord_x, knee_coord[1]+10), self.font, 0.6, self.COLORS['light_green'], 2, lineType=self.linetype)
                cv2.putText(frame, str(int(ankle_vertical_angle)), (ankle_text_coord_x, ankle_coord[1]), self.font, 0.6, self.COLORS['light_green'], 2, lineType=self.linetype)

                draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['SQUAT_COUNT']), 
                    pos=(int(frame_width*0.80), 20),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(18, 185, 0)
                )  

                draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_SQUAT']), 
                    pos=(int(frame_width*0.80), 60),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(221, 0, 0),
                )  
                
                self.state_tracker['DISPLAY_TEXT'][self.state_tracker['COUNT_FRAMES'] > self.thresholds['CNT_FRAME_THRESH']] = False
                self.state_tracker['COUNT_FRAMES'][self.state_tracker['COUNT_FRAMES'] > self.thresholds['CNT_FRAME_THRESH']] = 0    
                self.state_tracker['prev_state'] = current_state
        
        else:

            if self.flip_frame:
                frame = cv2.flip(frame, 1)

            end_time = time.perf_counter()
            self.state_tracker['INACTIVE_TIME'] += end_time - self.state_tracker['start_inactive_time']

            display_inactivity = False

            if self.state_tracker['INACTIVE_TIME'] >= self.thresholds['INACTIVE_THRESH']:
                self.state_tracker['SQUAT_COUNT'] = 0
                self.state_tracker['IMPROPER_SQUAT'] = 0
                cv2.putText(frame, 'Resetting SQUAT_COUNT due to inactivity!!!', (10, frame_height - 25), self.font, 0.7, self.COLORS['blue'], 2)
                display_inactivity = True

            self.state_tracker['start_inactive_time'] = end_time

            draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['SQUAT_COUNT']), 
                    pos=(int(frame_width*0.80), 20),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(18, 185, 0)
                )  

            draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_SQUAT']), 
                    pos=(int(frame_width*0.80), 60),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=(221, 0, 0),
                )  

            if display_inactivity:
                play_sound = 'reset_counters'
                self.state_tracker['start_inactive_time'] = time.perf_counter()
                self.state_tracker['INACTIVE_TIME'] = 0.0
                
            # Reset all other state variables
            
            self.state_tracker['prev_state'] =  None
            self.state_tracker['curr_state'] = None
            self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
            self.state_tracker['INCORRECT_POSTURE'] = False
            self.state_tracker['DISPLAY_TEXT'] = np.full((5,), False)
            self.state_tracker['COUNT_FRAMES'] = np.zeros((5,), dtype=np.int64)
            self.state_tracker['start_inactive_time_front'] = time.perf_counter()
                       
        return frame, play_sound
