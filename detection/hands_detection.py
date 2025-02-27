import mediapipe
import cv2
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands


class HandsDetector:
    def __init__(self):
        self.hands = handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2)


    def detect(self, frame):
        frame1 = cv2.resize(frame, (640, 480))
        
        results = self.hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
        
        if results.multi_hand_landmarks != None:
            for handLandmarks in results.multi_hand_landmarks:
                  drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)

        cv2.imshow('Object detector', frame1)
        cv2.waitKey(1)
        return results.multi_hand_landmarks != None
