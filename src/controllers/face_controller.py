import cv2

from models.face import Face

class FaceController:

    def __init__(self):        
        self.face_cascade_path = 'src/data/haarcascade/frontalface_default.xml'    
        self.eye_cascade_path = "src/data/haarcascade/eye.xml"
    
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(self.eye_cascade_path)
        
    def detect_face(self, frame):        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))        
        
        x, y, w, h = face[0]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (22, 192, 115), 2)

        eyes = []

        for (x, y, w, h) in face:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        return Face(face=face, eyes=eyes)
    
    