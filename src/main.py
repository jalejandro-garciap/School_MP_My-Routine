import cv2
from controllers.body_controller import BodyController
from controllers.camera_controller import CameraController
from controllers.exercise_controller import ExerciseController
from controllers.face_controller import FaceController
from controllers.rfid_controller import RfidController
from utils.timer import Timer
from utils.ui_utils import draw_text

def main():

    face_controller = FaceController()
    body_controller = BodyController()
    exercise_controller = ExerciseController()
    rfid_controller = RfidController()

    camera = CameraController()
    timer = Timer()    
    
    timer.start()
    rfid_controller.start_reading()

    while True:
        frame = camera.capture_frame()
        if frame is None:
            continue

        # 1. Waiting for the entry of an RFID card

        if not rfid_controller.scanned_card:
            msg = "Present your card"
            draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
            timer.restart()

        # 2. Request facial recognition

        if not face_controller.captured_face and rfid_controller.scanned_card:
            face = face_controller.detect_face(frame)        

            if face is not None:                
                if not timer.has_elapsed(6):
                    msg = f"Wait 5 seconds: { timer.elapsed_time() }"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    face_controller.faces.append(face)
                else:
                    face_controller.captured_face = True
                    timer.restart()
            else:
                msg = "Look at the camera"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()        

        # 3. Request body recognition
                
        if not body_controller.captured_body and face_controller.captured_face:
            body = body_controller.detect_body(frame)
            
            if body is not None:         
                if not timer.has_elapsed(6):
                    msg = f"Wait 5 seconds: { timer.elapsed_time() }"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    body_controller.bodies.append(body)
                else:
                    body_controller.captured_body = True
                    timer.restart()
            else:
                msg = "Get away from the camera"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()

        # 4. Select exercise
                
        if not exercise_controller.selected_exercise and body_controller.captured_body:
            hand = body_controller.detect_hand_gesture(frame)

            if hand is not None:
                if not timer.has_elapsed(6):
                    msg = f"Wait 5 seconds: { timer.elapsed_time() }"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    exercise_controller.hands.append(hand)
                else:
                    exercise_controller.selected_exercise = True
                    timer.restart()
            else:
                msg = "Shows hands on screen"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()

        # 5. Exercise assignment

        if not exercise_controller.exercise_started and exercise_controller.selected_exercise:   

            body = body_controller.analyze_body(frame,face_controller.faces)
            exercise_to_do = exercise_controller.analyze_selected_option()
            exercise = exercise_controller.assign_exercises(body, exercise_to_do)
            exercise_controller.exercise_started = True

            print(body)
            print(exercise)

        # 6. Validate exercise
            
        if not exercise_controller.exercise_done and exercise_controller.exercise_started:
            exercise_controller.run(frame, exercise)   
        
        # 7. Register in the database & pay ticket
            
            if exercise_controller.exercise_done:
                print("Fin del juego")
            
        # 8. Reset parameters

        cv2.imshow('Camera', frame)        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release_camera()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()