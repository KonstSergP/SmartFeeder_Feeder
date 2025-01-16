import argparse
import os

parser = argparse.ArgumentParser(description='Use arguments to change programm parameters')

parser.add_argument(
    '--smp',
    type=str, default=os.path.join("squirrel_model", "detect.tflite"),
    help='path to squirrel detection .tflite model'
)

parser.add_argument(
    '--slp',
    type=str, default=os.path.join("squirrel_model", "labelmap.txt"),
    help='path to squirrel detection model labelmap'
)

parser.add_argument(
    '--min-conf-threshhold',
    type=float, default=0.9,
    help='minimum confidence threshhold for squirrel detection model'
)

parser.add_argument(
    '--servo-pin',
    type=int, default=14,
    help='number of pin that connected with servo'
)

parser.add_argument(
    '--server-ip',
    type=str, default="192.168.1.74",
    help='ip address of server'
)

parser.add_argument(
    '--server-port',
    type=int, default=5000,
    help='server port'
)

parser.add_argument(
    '--width',
    type=int, default=640,
    help='width of video frame'
)

parser.add_argument(
    '--height',
    type=int, default=480,
    help='height of video frame'
)

parser.add_argument(
    "--debug", default=False, action="store_true",
    help="Enable debug mode")

args = parser.parse_args()
