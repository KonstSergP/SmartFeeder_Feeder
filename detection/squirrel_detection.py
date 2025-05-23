import tflite_runtime.interpreter as tflite
import cv2
import numpy as np
from settings.config import *


class SquirrelDetector:
    def __init__(self) -> None:
        self.interpreter = tflite.Interpreter(model_path=settings.squirrel_model_path)
        self.interpreter.allocate_tensors()
        
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        self.width, self.height = input_details[0]["shape"][1:3]
        self.input_index = input_details[0]['index']
        self.boxes_index = output_details[0]['index']
        self.classes_index = output_details[1]['index']
        self.scores_index = output_details[2]['index']
        
        with open(settings.squirrel_labels_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]


    def detect(self, frame) -> bool:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        self.interpreter.set_tensor(self.input_index, input_data)

        self.interpreter.invoke()

        boxes = self.interpreter.get_tensor(self.boxes_index)[0]
        classes = self.interpreter.get_tensor(self.classes_index)[0]
        scores = self.interpreter.get_tensor(self.scores_index)[0]

        found = False
        for i in range(len(scores)):

            if ((scores[i] > settings.min_conf_threshhold) and (scores[i] <= 1.0)):
                if (self.labels[int(classes[i])]) == "squirrel":
                    found = True
                    if not settings.show_preview: break

                # if show_preview
                ymin = int(max(1,(boxes[i][0] * settings.height)))
                xmin = int(max(1,(boxes[i][1] * settings.width)))
                ymax = int(min(settings.height,(boxes[i][2] * settings.height)))
                xmax = int(min(settings.width,(boxes[i][3] * settings.width)))
                
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                object_name = self.labels[int(classes[i])]
                label = '%s: %d%%' % (object_name, int(scores[i]*100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, labelSize[1] + 10)
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        if settings.show_preview:
            cv2.imshow('Object detector', frame)
            cv2.waitKey(1)
        return found


class CustomSquirrelDetector:
    """Class that uses our own tflite model for detecting squirrels"""
    def __init__(self) -> None:
        self.interpreter = tflite.Interpreter(model_path=settings.my_squirrel_model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_shape = self.input_details[0]['shape']
        self.input_height = self.input_shape[1]
        self.input_width = self.input_shape[2]
        self.input_dtype = self.input_details[0]['dtype']
        self.input_index = self.input_details[0]['index']
        self.output_index = self.output_details[0]['index']

    def detect(self, frame) -> bool:
        frame_resized = cv2.resize(frame, (self.input_width, self.input_height))
        rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        input_data = np.expand_dims(rgb_frame, axis=0).astype(self.input_dtype)
        
        self.interpreter.set_tensor(self.input_index, input_data)
        self.interpreter.invoke()
        prediction = self.interpreter.get_tensor(self.output_index)
        scores = prediction[0]
        
        max_score = np.max(scores)

        log.debug(f"Confidence: {max_score}")
        return max_score > 0.9
