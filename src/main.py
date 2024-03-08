import cv2
from controllers.body_controller import BodyController
from controllers.camera_controller import CameraController
from controllers.exercise_controller import ExerciseController
from controllers.face_controller import FaceController
from controllers.rfid_controller import RfidController
from database.database_operations import get_station_by_name, insert_history_record, recharge_passenger_balance
from utils.timer import Timer
from utils.ui_utils import draw_text

STATION_NAME = "CUCEI"

def show_status(frame, msg, minus):
    frame_height, frame_width = frame.shape[0], frame.shape[1]
    text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]
    pos_msg_h = frame_height - minus
    pos_msg_w = (frame_width - text_width) // 2            
    draw_text(frame, msg, pos=(pos_msg_w, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))

def show_results(frame, successful):    

    msg = "Congratulations you finished" if successful else "Luck for the next"
    color = (18, 185, 0) if successful else (10, 0, 255)

    if successful:
        show_status(frame, "Enjoy your free trip", 35)

    frame_height, frame_width = frame.shape[0], frame.shape[1]
    text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]
    pos_msg_h = frame_height // 2
    pos_msg_w = (frame_width - text_width) // 2
    draw_text(frame, msg, pos=(pos_msg_w, pos_msg_h), font_scale=0.8, text_color=(255, 255, 230), text_color_bg=color)

def main():

    face_controller = FaceController()
    body_controller = BodyController()
    exercise_controller = ExerciseController()
    rfid_controller = RfidController()

    station = get_station_by_name(STATION_NAME)

    camera = CameraController(1)
    timer = Timer()
    
    timer.start()
    rfid_controller.start_reading()


    while True:
        frame = camera.capture_frame()
        if frame is None:
            continue
        cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Camera', 832, 624)
        #frame_height, frame_width = frame.shape[0], frame.shape[1]
        
        #print("window_width: " + str(frame_width))
        #print("window_height: " + str(frame_height))

        # 1. Waiting for the entry of an RFID card

        if not rfid_controller.scanned_card:
            msg = "Present your card"
            draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))
            
            if rfid_controller.message is not None:
                draw_text(frame, rfid_controller.message, pos=(25, 65), font_scale=0.7, text_color=(255, 255, 255), text_color_bg=(10, 0, 255))
            
            timer.restart()

        # 2. Request facial recognition

        if not face_controller.captured_face and rfid_controller.scanned_card:
            face = face_controller.detect_face(frame)        

            show_status(frame,"Face Analysis", 35)

            if face is not None:                
                if not timer.has_elapsed(5):
                    msg = f"Wait { 5 - timer.elapsed_time() } seconds"
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
            
            show_status(frame,"Body Analysis", 35)            

            if body is not None:         
                if not timer.has_elapsed(5):
                    msg = f"Wait { 5 - timer.elapsed_time() } seconds"
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

            show_status(frame,"Select with your hands", 35) 
            frame_height, frame_width = frame.shape[0], frame.shape[1]
            pos_msg_h = frame_height // 2
            pos_msg_w_1 = 25   
            msg = "Sentadillas"        
            draw_text(frame, msg, pos=(pos_msg_w_1, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))   
            msg = "Lagartijas"
            text_width = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0][0]   
            pos_msg_w_2 = frame_width - text_width      
            draw_text(frame, msg, pos=(pos_msg_w_2, pos_msg_h), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(255, 191, 0))          

            if hand is not None:
                if not timer.has_elapsed(3):
                    msg = f"Wait { 3 - timer.elapsed_time() } seconds"
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
            timer.restart() 

        # 6. Validate exercise
            
        if not exercise_controller.exercise_done and exercise_controller.exercise_started:
            
            if not timer.has_elapsed(60): # Start counting time for each exercise: 1 minute max
                
                show_status(frame,exercise.type,35)  

                msg = f"Time to finish: { 60 - timer.elapsed_time() }"
                draw_text(frame, msg, pos=(25, 25), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))

                msg = f"Target: { exercise.target_reps }"
                draw_text(frame, msg, pos=(25, 70), font_scale=0.7, text_color=(255, 255, 230), text_color_bg=(18, 185, 0))

            else:
                exercise_controller.exercise_done = True

            exercise_controller.run(frame, exercise)
        
        # 7. Register in the database & pay ticket
            
        if not exercise_controller.show_result and exercise_controller.exercise_done:    
            challenge_completed = exercise_controller.rep_count == exercise.target_reps        
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
        
        cv2.imshow('Camera', frame)        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release_camera()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()