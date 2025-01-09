import os
import cv2
import numpy as np
import time
from threading import Thread

from tflite_runtime.interpreter import Interpreter


class VideoStream:

    """Camera object that controls video streaming from the Picamera"""

    def __init__(self,resolution=(640,480),framerate=30):

        self.stream = cv2.VideoCapture(0)

        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(3,resolution[0])
        self.stream.set(4,resolution[1])

        # Read first frame from the stream

        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self


    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return
            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()


    def read(self):
        return self.frame


    def stop(self):
        self.stopped = True


MODEL_NAME = "squirrel_model"

GRAPH_NAME = "detect.tflite"

LABELMAP_NAME = "labelmap.txt"

min_conf_threshold = 0.5

imW, imH = 1280, 720


CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)


with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]


interpreter = Interpreter(model_path=PATH_TO_CKPT)


interpreter.allocate_tensors()


input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]


# Initialize video stream

videostream = VideoStream(resolution=(imW,imH),framerate=30).start()

time.sleep(1)


while True:

    frame1 = videostream.read()

    frame = frame1.copy()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame_resized = cv2.resize(frame_rgb, (width, height))

    input_data = np.expand_dims(frame_resized, axis=0)

    interpreter.set_tensor(input_details[0]['index'],input_data)

    interpreter.invoke()

    # Retrieve detection results

    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects

    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects

    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

    for i in range(len(scores)):

        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()

            ymin = int(max(1,(boxes[i][0] * imH)))

            xmin = int(max(1,(boxes[i][1] * imW)))

            ymax = int(min(imH,(boxes[i][2] * imH)))

            xmax = int(min(imW,(boxes[i][3] * imW)))

            
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)


            # Draw label

            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index

            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'

            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size

            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window

            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in

            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

videostream.stop()
