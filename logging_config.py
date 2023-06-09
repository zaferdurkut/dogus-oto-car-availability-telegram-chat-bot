import logging
import sys


def setup_logger(name: str, level: int) -> logging.Logger:
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-4s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S.%s",
    )
    tmp_path = "/tmp/tmp.log"
    handler = logging.FileHandler(tmp_path)
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
