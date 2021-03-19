import logging
import os


logger_global = None

log_format_args={
    "fmt": "%(asctime)s %(message)s",
    "datefmt": "[%Y-%m-%d %H:%M:%S]"
}


def initialize(log_global_path):

    global logger_global

    formatter = logging.Formatter(**log_format_args)

    logger_global = logging.getLogger("logger_main")
    logger_global.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger_global.addHandler(ch)

    fh_main = logging.FileHandler(log_global_path)
    fh_main.setFormatter(formatter)
    logger_global.addHandler(fh_main)


def debug_global(message):

    if logger_global is None:
        raise Exception("Logger must be first initialized")

    logger_global.debug(message)


def info_global(message):

    if logger_global is None:
        raise Exception("Logger must be first initialized")

    logger_global.info(message)


def exception_global(ex: Exception):

    if logger_global is None:
        raise Exception("Logger must be first initialized")

    logger_global.exception(ex)


def create_new_logger(log_path):

    global logger_global

    log_folder = "/".join(log_path.split("/")[:-1])

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    with open(log_path, "a+"):
        pass

    formatter = logging.Formatter(**log_format_args)

    logger_custom = logging.getLogger(log_path)
    logger_custom.setLevel(logging.DEBUG)

    fh_training = logging.FileHandler(log_path)
    fh_training.setFormatter(formatter)
    logger_custom.addHandler(fh_training)

    return logger_custom