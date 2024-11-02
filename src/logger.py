import logging

logger = logging.getLogger("JARVIS")
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("jarvis.log")
formatter = logging.Formatter("%(asctime)s %(message)s")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
