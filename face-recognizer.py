from deepface import DeepFace
import cv2
import time
from config import config

model = DeepFace.build_model("Facenet")
cap = cv2.VideoCapture(0)
last_unverified = 0

while True:
    ret, frame = cap.read()  # Read a frame from the webcam

    try:
        verified = False
        # Detect faces using the DeepFace model
        detected_faces = DeepFace.extract_faces(frame)

        # Loop through each detected face
        for face in detected_faces:
            area = face["facial_area"]
            # Draw a rectangle around the face
            x, y, w, h = area['x'], area['y'], area['w'], area['h']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1) 
            verified = False
            
            # Find known faces
            dfs = DeepFace.find(
                img_path=frame[y:y+h, x:x+w],
                db_path=".cache/deepface-db",
                enforce_detection=False,
                silent=True,
            )
            # Loop through each known face
            for df in dfs:
                if str(df["identity"][0]) == config["owner"]:
                    verified = True
                    if time.time() - last_unverified > 5:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        cv2.putText(frame, "N3RDIUM", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
            # Detect emotion
            try:
                objs = DeepFace.analyze(
                    img_path=frame[y:y+h, x:x+w],
                    actions = ['emotion'],
                    silent=True,
                )
                # Display emotion in smaller text above the face
                cv2.putText(frame, objs[0]['dominant_emotion'], (x, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 255, 255), 1)
            except:
                pass
                    
        if not verified:
            last_unverified = time.time()

    except KeyboardInterrupt:
        break
    except:
        pass
    # Display the frame with recognized faces
    cv2.imshow("Real-time Face Recognition", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
