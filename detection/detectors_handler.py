from .hands_detection import HandsDetector
from .squirrel_detection import SquirrelDetector, MyDetector


class DetectorsHandler:
    """Coordinates different computer vision detectors."""
    def __init__(self) -> None:
        self._squirrel_detector = SquirrelDetector()
        #self._squirrel_detector = MyDetector()
        self._hands_detector    = HandsDetector()
        self._frame = None


    def update_frame(self, frame) -> None:
        """Update the current frame that will be analyzed by detectors."""
        self._frame = frame


    def detect_squirrel(self) -> bool:
        """
        Run squirrel detection on the current frame.\n
        Returns True if a squirrel is detected, False otherwise
        """
        return self._squirrel_detector.detect(self._frame)
    
    
    def detect_hands(self) -> bool:
        """
        Run hands detection on the current frame.\n
        Returns True if hands are detected, False otherwise
        """
        return self._hands_detector.detect(self._frame)
