import tflite_runtime.interpreter as tflite

from config import *

class SquirrelDetector:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path=Config.SQUIRREL_MODEL_PATH)
        self.interpreter.allocate_tensors()

    def detect(self, frame):
        # Placeholder logic for detection
        return False


class HandsDetector:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path=Config.HANDS_MODEL_PATH)
        self.interpreter.allocate_tensors()

    def detect(self, frame):
        # Placeholder logic for detection
        return False
