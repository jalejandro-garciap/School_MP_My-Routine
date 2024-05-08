import cv2
from controllers.body_controller import BodyController
from controllers.camera_controller import CameraController
from controllers.exercise_controller import ExerciseController
from controllers.face_controller import FaceController
from controllers.rfid_controller import RfidController
from database.database_operations import get_station_by_name, insert_history_record, recharge_passenger_balance
from utils.timer import Timer
from utils.ui_utils import draw_text
from utils.sound_effects import play_sound

STATION_NAME = "CUCEI"

def show_status(frame, msg, minus):
    frame_height, frame_width = frame.shape[0], frame.shape[1]
    text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]
    pos_msg_h = frame_height - minus
    pos_msg_w = (frame_width - text_width) // 2            
    draw_text(frame, msg, pos=(pos_msg_w, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))

def show_results(frame, successful):    

    msg = "FELICIDADES, HAS TERMINADO!" if successful else "SUERTE PARA LA PROXIMA"
    color = (18, 185, 0) if successful else (10, 0, 255)

    if successful:
        show_status(frame, "DISFRUTA TU PASE GRATIS", 35)

    frame_height, frame_width = frame.shape[0], frame.shape[1]
    text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]
    pos_msg_h = frame_height // 2
    pos_msg_w = (frame_width - text_width) // 2
    draw_text(frame, msg, pos=(pos_msg_w, pos_msg_h), font_scale=1, text_color=(255, 255, 230), text_color_bg=color)

def main():

    face_controller = FaceController()
    body_controller = BodyController()
    exercise_controller = ExerciseController()
    rfid_controller = RfidController()

    station = get_station_by_name(STATION_NAME)

    camera = CameraController(0)
    timer = Timer()
    
    timer.start()
    rfid_controller.start_reading()

    sound_played = False

    while True:
        frame = camera.capture_frame()
        if frame is None:
            continue
        
        # 1. Waiting for the entry of an RFID card

        if not rfid_controller.scanned_card:
            msg = "PRESENTA TU TARJETA"
            draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
            
            if rfid_controller.message is not None:
                draw_text(frame, rfid_controller.message, pos=(25, 65), font_scale=0.7, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
            
            timer.restart()

        # 2. Request facial recognition

        if not face_controller.captured_face and rfid_controller.scanned_card:
            face = face_controller.detect_face(frame)        

            show_status(frame,"ANALISIS FACIAL", 35)

            if face is not None:                
                if not timer.has_elapsed(3):
                    msg = f"ESPERA { 3 - timer.elapsed_time() } SEGUNDOS"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    face_controller.faces.append(face)
                else:
                    face_controller.captured_face = True
                    timer.restart()
            else:
                msg = "MIRA A LA CAMARA"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()        

        # 3. Request body recognition
                
        if not body_controller.captured_body and face_controller.captured_face:
            body = body_controller.detect_body(frame)
            
            show_status(frame,"ANALISIS CORPORAL", 35)            

            if body is not None:         
                if not timer.has_elapsed(3):
                    msg = f"ESPERA { 3 - timer.elapsed_time() } SEGUNDOS"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    body_controller.bodies.append(body)
                else:
                    body_controller.captured_body = True
                    timer.restart()
            else:
                msg = "ALEJATE DE LA CAMARA"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()

        # 4. Select exercise
                
        if not exercise_controller.selected_exercise and body_controller.captured_body:
            hand = body_controller.detect_hand_gesture(frame)

            show_status(frame,"ESCOGE CON TUS MANOS", 35) 
            frame_height, frame_width = frame.shape[0], frame.shape[1]
            pos_msg_h = frame_height // 2
            pos_msg_w_1 = 25   
            msg = "SENTADILLAS"        
            draw_text(frame, msg, pos=(pos_msg_w_1, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))   
            msg = "LAGARTIJAS"
            text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]   
            pos_msg_w_2 = frame_width - text_width      
            draw_text(frame, msg, pos=(pos_msg_w_2, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))          

            if hand is not None:
                if not timer.has_elapsed(3):
                    msg = f"ESPERA { 3 - timer.elapsed_time() } SEGUNDOS"
                    draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
                    exercise_controller.hands.append(hand)
                else:
                    exercise_controller.selected_exercise = True
                    timer.restart()
            else:
                msg = "MUESTRA TU MANO EN PANTALLA"
                draw_text(frame, msg, pos=(30, 20), font_scale=0.8, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
                timer.restart()

        # 5. Exercise assignment

        if not exercise_controller.exercise_started and exercise_controller.selected_exercise:   

            if not body_controller.analysis_started:
                body_controller.analyze_body(frame,face_controller.faces)

            elif body_controller.analysis_finished:                

                camera.change_camera()
                body = body_controller.body
                exercise_to_do = exercise_controller.analyze_selected_option()
                exercise = exercise_controller.assign_exercises(body, exercise_to_do)
                exercise_controller.exercise_started = True                

                print(body)
                print(exercise)
                timer.restart()            

        # 6. Validate exercise
            
        if not exercise_controller.exercise_done and exercise_controller.exercise_started:
            
            if not timer.has_elapsed(60): # Start counting time for each exercise: 1 minute max
                
                if(60 - timer.elapsed_time() == 5) and not sound_played : # 5 Seconds left?
                    play_sound("countdown")
                    sound_played = True

                msg = f"TIEMPO RESTANTE: { 60 - timer.elapsed_time() }"
                draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))

                msg = f"OBJETIVO: { exercise.target_reps }"
                draw_text(frame, msg, pos=(25, 70), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))

            else:
                exercise_controller.exercise_done = True

            exercise_controller.run(frame, exercise)
        
        # 7. Register in the database & pay ticket
            
        if not exercise_controller.show_result and exercise_controller.exercise_done:    
            challenge_completed = exercise_controller.rep_count == exercise.target_reps        

            if challenge_completed:
                play_sound("winner")
            else:
                play_sound("loser")

            insert_history_record(
                challenge_completed=challenge_completed,
                duration=timer.elapsed_time(),
                exercise=exercise.type,
                repetitions_done=exercise_controller.rep_count,
                target_reps=exercise.target_reps,
                passenger_id=rfid_controller.passenger.id,
                station_id=station.id
                )
            timer.restart()
            recharge_passenger_balance(rfid_controller.passenger)
            exercise_controller.show_result = True            

        # 8. Finish
            
        if exercise_controller.show_result:
            if not timer.has_elapsed(10):
                show_results(frame,challenge_completed)
            else:                
                face_controller = FaceController()
                body_controller = BodyController()
                exercise_controller = ExerciseController()
                rfid_controller = RfidController()
                rfid_controller.start_reading()
                timer.restart()
        
        cv2.imshow('Mi rutina', frame)        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release_camera()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()