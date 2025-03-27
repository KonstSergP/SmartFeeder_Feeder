import logging
import sys
import shelve
from dynaconf import Dynaconf


settings = Dynaconf(
    settings_files=["./settings/settings.toml"]
)

from .argument_parser import update_config
update_config()


log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(handler)
log.setLevel(settings.log_level)


def get_feeder_id():
    with shelve.open("./settings/connection_info") as info:
        if "feeder_id" in info:
            if not settings.reset_id:
                return info["feeder_id"]
            del info["feeder_id"]
    return None


def set_feeder_id(feeder_id):
    try:
        with shelve.open("./settings/connection_info") as info:
            info["feeder_id"] = feeder_id
        log.info(f"Сохранен новый id: {feeder_id}")
    except Exception as e:
        log.error(f"Ошибка сохранения id: {e}")
        raise RuntimeError("Ошибка сохранения id")


def get_socket_address():
    if settings.mode == "production":
        return settings.server_host
    return f"{settings.server_host}:{settings.server_port}"
