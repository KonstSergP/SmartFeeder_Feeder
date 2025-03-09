from .hands_detection import HandsDetector
from .squirrel_detection import SquirrelDetector, MyDetector


class DetectorsHandler:
    def __init__(self):
        self._squirrel_detector = SquirrelDetector()
        #self._squirrel_detector = MyDetector()
        self._hands_detector    = HandsDetector()
        self._frame = None

    def update_frame(self, frame):
        self._frame = frame

    def detect_squirrel(self):
        return self._squirrel_detector.detect(self._frame)
    
    def detect_hands(self):
        return self._hands_detector.detect(self._frame)
