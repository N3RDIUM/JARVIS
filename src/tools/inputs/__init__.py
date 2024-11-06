import importlib
import logging
import os
import sys

from logger import logger

sys.path.append(os.path.dirname(__file__))

inputs = []
BLACKLIST = ["__init__"]


class InputManager:
    def __init__(self):
        self.inputs = []
        self.input_queue = []

    def register_inputs(self):
        for file in os.listdir(os.path.dirname(__file__)):
            if not file.endswith(".py") or file.strip(".py") in BLACKLIST:
                continue
            module = importlib.import_module(file.strip(".py"))
            self.inputs.append(module.input_export(parent=self))
            logger.log(
                logging.DEBUG,
                f"DEBUG [ inputs    ]  Registered input `{module.input_export.name}`",
            )

    def begin_streams(self):
        logger.log(
            logging.DEBUG,
            "DEBUG [ inputs    ]  Beginning input streams...",
        )
        for input in self.inputs:
            input.begin_stream()

    def kill_streams(self):
        logger.log(
            logging.DEBUG,
            "DEBUG [ inputs    ]  Killing input streams...",
        )
        for input in self.inputs:
            input.kill_stream()
