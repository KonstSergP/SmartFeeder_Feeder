import tflite_runtime.interpreter as tflite
import cv2
import numpy as np

from config import *

class SquirrelDetector:
    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path=Config.SQUIRREL_MODEL_PATH)
        self.interpreter.allocate_tensors()
        
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        self.width, self.height = input_details[0]["shape"][1:3]
        self.input_index = input_details[0]['index']
        self.boxes_index = output_details[0]['index']
        self.classes_index = output_details[1]['index']
        self.scores_index = output_details[2]['index']
        
        with open(Config.SQUIRREL_LABELS_PATH, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

    def detect(self, frame1):
        frame = frame1.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        self.interpreter.set_tensor(self.input_index, input_data)

        self.interpreter.invoke()

        # Retrieve detection results

        boxes = self.interpreter.get_tensor(self.boxes_index)[0] # Bounding box coordinates of detected objects

        classes = self.interpreter.get_tensor(self.classes_index)[0] # Class index of detected objects

        scores = self.interpreter.get_tensor(self.scores_index)[0] # Confidence of detected objects

        found = False
        for i in range(len(scores)):

            if ((scores[i] > Config.MIN_CONF_THRESHHOLD) and (scores[i] <= 1.0)):
                if (self.labels[int(classes[i])]) == "squirrel": found = True
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()

                ymin = int(max(1,(boxes[i][0] * Config.FRAME_SIZE[1])))

                xmin = int(max(1,(boxes[i][1] * Config.FRAME_SIZE[0])))

                ymax = int(min(Config.FRAME_SIZE[1],(boxes[i][2] * Config.FRAME_SIZE[1])))

                xmax = int(min(Config.FRAME_SIZE[0],(boxes[i][3] * Config.FRAME_SIZE[0])))
                
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                object_name = self.labels[int(classes[i])] # Look up object name from "labels" array using class index

                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'

                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size

                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window

                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in

                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
        cv2.imshow('Object detector', frame)
        cv2.waitKey(1)
        return found
