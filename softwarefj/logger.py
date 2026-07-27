import logging
import os

_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "eventos.log")

os.makedirs(_LOG_DIR, exist_ok=True)

logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler_archivo = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.WARNING)
    handler_consola.setFormatter(formato)

    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)


def get_log_path() -> str:
    return _LOG_FILE
