import sys
import cv2
import pyautogui
import time
import math
import numpy as np
import mediapipe as mp
from collections import Counter
from process_frame import ProcessFrame  # Ajusta los nombres de módulos, clases y funciones según sea necesario
from thresholds import get_thresholds_beginner, get_thresholds_pro
from utils import get_mediapipe_pose, draw_text

# Estados de la ejecución
WAITING = 1
ANALYZING = 2
DISPLAYING = 3
CHOOSING = 4

# Modelos preentrenados
age_model = "models/age_deploy.prototxt"
age_weights = "models/age_net.caffemodel"
gender_model = "models/gender_deploy.prototxt"
gender_weights = "models/gender_net.caffemodel"
eye_cascade_path = "data/haarcascade/eye.xml"
face_cascade_path = 'data/haarcascade/frontalface_default.xml'

# Listas con posibles edades y géneros que el modelo puede predecir
AGE_LIST = ['0-2', '4-6', '8-12', '15-20', '25-32', '38-43', '48-53', '60-100']
GENDER_LIST = ['Hombre', 'Mujer']

# Obtiene el tamaño del monitor principal
screen_width, screen_height = pyautogui.size()

# Calcula las coordenadas de la mitad e inferior de la pantalla
middle_x = screen_width // 18
middle_y = screen_height // 18
bottom_y = screen_height - 650
margin_y = screen_height - 620

# Establece el tamaño de la ventana al tamaño del monitor
cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Declaración de funciones
def load_models():
    age_net = cv2.dnn.readNet(age_model, age_weights)
    gender_net = cv2.dnn.readNet(gender_model, gender_weights)
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    return age_net, gender_net, face_cascade
    
def get_frame(cap):
    ret, frame = cap.read()
    if not ret:
        print("No se logro grabar la imagen")
        return None
    frame = cv2.flip(frame, 1)
    return frame

def get_landmark_coordinates(landmarks, landmark):
    # Obtiene las coordenadas de un punto clave específico.
    return [landmarks[landmark.value].x, landmarks[landmark.value].y]
    
def detect_face(frame, face_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def detect_eyes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))    
    
    eyes = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    return eyes

def detect_age_gender_height(face, frame, age_net, gender_net):
    x, y, w, h = face
    face_blob = cv2.dnn.blobFromImage(frame[y:y+h, x:x+w], 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
    
    gender_net.setInput(face_blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]
    
    age_net.setInput(face_blob)
    age_preds = age_net.forward()
    age = AGE_LIST[age_preds[0].argmax()]

    eyes = detect_eyes(frame)
    distance_between_eyes = calculate_distance_between_eyes(eyes)

    if distance_between_eyes is not None:
        distance_in_cm = distance_between_eyes * 0.01 # Ajusta este valor según la relación entre la distancia en píxeles y centímetros
        height = distance_in_cm * 1.5 # Ajusta este valor según la relación entre la distancia en centímetros y la altura
    else:
        height = None

    return age, gender, height

def detect_hand_gesture(landmarks):

    mp_hands = mp.solutions.hands

    # Obtiene las coordenadas de los landmarks de interés
    index_tip = [landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x,
                 landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y]
    index_mcp = [landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x,
                 landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y]
    middle_mcp = [landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x,
                  landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y]
    ring_mcp = [landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].x,
                landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y]
    pinky_mcp = [landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x,
                 landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y]
    wrist = [landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
             landmarks.landmark[mp_hands.HandLandmark.WRIST].y]

    # Verifica si el dedo índice está extendido y los otros dedos están cerrados
    if (index_tip[1] < index_mcp[1] and
            middle_mcp[1] < ring_mcp[1] < pinky_mcp[1]):
        # Si el dedo índice está a la izquierda del centro de la muñeca, la mano está apuntando a la izquierda
        if index_tip[0] < wrist[0]:
            return "left"
        # Si el dedo índice está a la derecha del centro de la muñeca, la mano está apuntando a la derecha
        elif index_tip[0] > wrist[0]:
            return "right"

    return None

def calculate_distance_between_eyes(eyes):
    if len(eyes) == 2:
        center_left_eye = (eyes[0][0] + eyes[0][2] // 2, eyes[0][1] + eyes[0][3] // 2)
        center_right_eye = (eyes[1][0] + eyes[1][2] // 2, eyes[1][1] + eyes[1][3] // 2)

        distance = np.sqrt((center_left_eye[0] - center_right_eye[0]) ** 2 +
                           (center_left_eye[1] - center_right_eye[1]) ** 2)

        return distance
    else:
        return None

def calculate_distance(x1, y1, x2, y2):
    # Calcula la distancia euclidiana entre dos puntos.
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def evaluate_complexion(ratio):
    if ratio < 1.45:
        return "Endomorfo"
    elif ratio > 1.85:
        return "Ectomorfo"
    else:
        return "Mesomorfo"

def estimate_complexion(cap):

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                landmarks = results.pose_landmarks.landmark

                left_shoulder = get_landmark_coordinates(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
                right_shoulder = get_landmark_coordinates(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER)
                left_hip = get_landmark_coordinates(landmarks, mp_pose.PoseLandmark.LEFT_HIP)
                right_hip = get_landmark_coordinates(landmarks, mp_pose.PoseLandmark.RIGHT_HIP)

                shoulder_distance = calculate_distance(*left_shoulder, *right_shoulder)
                waist_distance = calculate_distance(*left_hip, *right_hip)

                if waist_distance == 0:
                    continue

                ratio = shoulder_distance / waist_distance
                complexion = evaluate_complexion(ratio)

                return frame, complexion
            
def print_results(gender_mode, age_mode, height_mode, complexion_mode):
    print(f"Sexo: {gender_mode}")
    print(f"Edad: {age_mode}")
    print(f"Altura: {height_mode}")
    print(f"Complexion: {complexion_mode}")

def assign_exercises_and_rpm(age, gender, complexion, height):
    # Lista de ejercicios asignados y RPM objetivo para bicicleta de spinning
    exercise_goal = 0
    rpm_target = 0
    is_pro = False
    
    print_results(gender, age, height, complexion)

    # Verificar si la persona es apta para ejercicios
    if '60-100' in age:
        return "No apto para ejercicios. Consulta a un médico.", rpm_target
    
    # Asignar ejercicios y RPM objetivo basándose en la complexión de la persona
    if complexion == "Endomorfo":
        exercise_goal = 5
        rpm_target = 60
    elif complexion == "Mesomorfo":
        exercise_goal = 10
        rpm_target = 80
        is_pro = True
    elif complexion == "Ectomorfo":
        exercise_goal = 15
        rpm_target = 100
    
    # Ajustar ejercicios y RPM objetivo basándose en el género
    if gender == "Mujer":
        rpm_target -= 10
        is_pro = False
    
    # Ajustar ejercicios y RPM objetivo basándose en la edad
    if '48-53' in age or '38-43' in age:
        is_pro = False
        exercise_goal = 3
        rpm_target = 50
    
    return exercise_goal, rpm_target, is_pro

def main():

    physical_traits = []
    body_data = []
    start_time = None
    state = WAITING
    chosen_action = None
    
    try:
        cap = cv2.VideoCapture(0) # Inicializa la cámara
    except Exception as e:
        print(f"Error al inicializar la cámara: {e}")
        sys.exit()

    age_net, gender_net, face_cascade = load_models()

    mp_hands = mp.solutions.hands
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            frame = get_frame(cap)
            if frame is not None:
                faces = detect_face(frame, face_cascade)
                
                # Estado: WAITING
                if state == WAITING:
                    if len(faces) > 0:
                        # Dibujar rectángulo alrededor del rostro
                        x, y, w, h = faces[0]
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (22, 192, 115), 2)
                        
                        if start_time is None:
                            start_time = time.time()
                            
                        elapsed_time = int(time.time() - start_time)
                        if elapsed_time < 5:

                            texto = f"Espera: {5 - elapsed_time} seg"
                            draw_text(frame, texto, 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))

                            # Analizar rostro
                            age, gender, height = detect_age_gender_height(faces[0], frame, age_net, gender_net)
                            if height is not None:
                                physical_traits.append((age, gender, height))
                        else:
                            state = ANALYZING
                            start_time = None
                    else:
                        draw_text(frame, "Mira a la pantalla", 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                        start_time = None  # Reiniciar el cronómetro cuando no se detecta ningún rostro
                        
                # Estado: ANALYZING
                elif state == ANALYZING:
                    if start_time is None:
                        start_time = time.time()
                        
                    elapsed_time = int(time.time() - start_time)
                    if elapsed_time < 8:
                        if elapsed_time < 3:  # Tiempo de advertencia
                            draw_text(frame, "Alejate de la pantalla", 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                        
                        else:                          
                            # Analizar cuerpo
                            frame, complexion = estimate_complexion(cap)  # Recibe el frame modificado
                            body_data.append(complexion)
                            
                            texto = f"Espera: {8 - elapsed_time} seg"
                            draw_text(frame, texto, 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))
                            
                    else:
                        state = DISPLAYING
                        start_time = None
                        
                # Estado: DISPLAYING
                elif state == DISPLAYING:
                    # Calcular y mostrar resultados
                    age_mode, gender_mode, height_mode = Counter(physical_traits).most_common(1)[0][0]
                    complexion_mode = Counter(body_data).most_common(1)[0][0]
                    
                    # Asignar ejercicios y RPM objetivo
                    exercise_goal, rpm_target, is_pro = assign_exercises_and_rpm(age_mode, gender_mode, complexion_mode, height_mode)
                
                    state = CHOOSING

                # Estado: CHOOSING
                elif state == CHOOSING:

                    #draw_text(frame, "Escoge: <- Bicicleta | Ejercicio ->", 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(middle_x, bottom_y), font_scale=0.7, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))

                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(image)
                    
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            gesture = detect_hand_gesture(hand_landmarks)
                            if gesture == "left":
                                chosen_action = "spinning_target"
                                break
                            elif gesture == "right":
                                chosen_action = "assigned_exercises"
                                break

                    if chosen_action == "spinning_target" or chosen_action == "assigned_exercises":
                        text_action=f"Accion Elegida: {chosen_action}"
                    elif chosen_action == None:
                        draw_text(frame, "Escoge: <- Bicicleta | Ejercicio ->", 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(middle_x, bottom_y), font_scale=0.7, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))

                    if chosen_action == "spinning_target":
                        bicycle = f"RPM Spinning: {rpm_target}"
                        draw_text(frame, bicycle, 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))
                    elif chosen_action == "assigned_exercises":
                        squat = f"Sentadillas: {exercise_goal}"
                        draw_text(frame, squat, 8, font=cv2.FONT_HERSHEY_SIMPLEX, pos=(30, 20), font_scale=0.8, font_thickness=2, text_color=(255, 255, 255), text_color_bg=(255, 150, 0))
                        

                    if(chosen_action == "assigned_exercises"):

                        mp_pose = mp.solutions.pose
                        pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True)

                        # Configura los umbrales según el nivel de habilidad
                        thresholds = get_thresholds_pro() if is_pro else get_thresholds_beginner()
                        
                        # Crea una instancia de la clase ProcessFrame
                        processor = ProcessFrame(thresholds)

                        # Crea una instancia de la clase ProcessFrame
                        processor = ProcessFrame(thresholds)
                        # Procesa el frame y obtén retroalimentación
                        frame, feedback = processor.process(frame, pose)

                        if processor.squat_count >= exercise_goal:
                            print("¡Límite de sentadillas alcanzado!")
                            break

                        # Muestra la retroalimentación en el frame
                        draw_text(frame, feedback)
                    
                    #if chosen_action:
                        #cv2.putText(frame, f"Accion Elegida: {chosen_action}", (middle_x, margin_y), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 1)

                cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()