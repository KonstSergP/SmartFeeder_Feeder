import logging
import sys
import shelve
from dynaconf import Dynaconf
from typing import Optional


# This creates a settings object that can be imported throughout the application
settings = Dynaconf(
    settings_files=["./settings/settings.toml"]
)

# Import for applying command-line arguments
from .argument_parser import update_config
update_config()


# Configure logger
log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(handler)
log.setLevel(settings.log_level)


def get_feeder_id() -> Optional[str]:
    try:
        with shelve.open("./settings/connection_info") as info:
            if "feeder_id" in info:
                if not settings.reset_id:
                    return info["feeder_id"]
                del info["feeder_id"]
        return None
    except Exception as e:
        log.error(f"Error while getting id", exc_info=True)
        return None


def set_feeder_id(feeder_id: str) -> None:
    try:
        with shelve.open("./settings/connection_info") as info:
            info["feeder_id"] = feeder_id
        log.info(f"Сохранен новый id: {feeder_id}")
    except Exception as e:
        log.error(f"Ошибка сохранения id: {e}")
        raise RuntimeError("Ошибка сохранения id")


def get_socket_address() -> str:
    """Get the socket address for connections"""
    if settings.mode == "production":
        return settings.server_host
    return f"{settings.server_host}:{settings.server_port}"
