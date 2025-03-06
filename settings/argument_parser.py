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
    '--server-ip',
    type=str, default=settings.server_ip,
    help='ip address of server'
)

parser.add_argument(
    '--server-port',
    type=int, default=settings.server_port,
    help='server port'
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

args = parser.parse_args()

def update_config():
    settings.update(vars(args))
