from .config import settings
import argparse


parser = argparse.ArgumentParser(description='Use arguments to change programm parameters')

parser.add_argument(
    '--smp',
    type=str, default=settings.squirrel_model_path,
    help='path to squirrel detection .tflite model',
    dest="squirrel_model_path"
)

parser.add_argument(
    '--slp',
    type=str, default=settings.squirrel_labels_path,
    help='path to squirrel detection model labelmap',
    dest="squirrel_labelmap_path"
)

parser.add_argument(
    '--min-conf-threshhold',
    type=float, default=settings.min_conf_threshhold,
    help='minimum confidence threshhold for squirrel detection model'
)

parser.add_argument(
    '--servo-pin',
    type=int, default=settings.servo_pin,
    help='number of pin that connected with servo'
)

parser.add_argument(
    '--servo-speed',
    type=str, default=settings.servo_speed,
    choices=["slow", "medium", "fast"],
    help='speed of servo motor slow/medium/fast'
)

parser.add_argument(
    '--server-host',
    type=str, default=settings.server_host,
    help='ip address or domain name of server'
)

parser.add_argument(
    '--server-port',
    type=int, default=settings.server_port,
    help='server port'
)

parser.add_argument(
    '--reset-id',
    default=False,
    action='store_true',
    help='reset saved feeder id to ask new from server',
)

parser.add_argument(
    '--no-server',
    default=settings.online_mode,
    action='store_false',
    help='enable offline mode',
    dest='online_mode'
)

parser.add_argument(
    '--width',
    type=int, default=settings.width,
    help='width of video frame'
)

parser.add_argument(
    '--height',
    type=int, default=settings.height,
    help='height of video frame'
)

parser.add_argument(
    "--log-level", default=settings.log_level,
    help="Change log level")


camera_mode_group = parser.add_mutually_exclusive_group()
camera_mode_group.add_argument(
    '--enable-mode-control', 
    action='store_true',
    dest='enable_camera_mode_control',
    help='enable camera mode control'
)
camera_mode_group.add_argument(
    '--disable-mode-control', 
    action='store_false',
    dest='enable_camera_mode_control',
    help='disable camera mode control'
)
parser.set_defaults(enable_camera_mode_control=settings.enable_camera_mode_control)


parser.add_argument(
    '--camera-mode-pin',
    type=int, default=settings.camera_mode_pin,
    help='GPIO pin controlling IR filter',
)

parser.add_argument(
    '--camera-mode',
    type=str, default=settings.camera_mode,
    choices=["auto", "day", "night"],
    help='night mode: auto (light sensor), day, or night',
)

parser.add_argument(
    '--fps',
    type=int, default=settings.fps,
    help='Framerate of video and stream',
)


args = parser.parse_args()

def update_config() -> None:
    settings.update(vars(args))
