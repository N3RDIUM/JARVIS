import importlib
import logging
import os
import sys

from logger import logger

sys.path.append(os.path.dirname(__file__))

BLACKLIST = ["__init__"]


class Toolchain:
    def __init__(self):
        self.tools = []
        self.function_map = {}

    def register_tools(self):
        for file in os.listdir(os.path.dirname(__file__)):
            if not file.endswith(".py") or file.strip(".py") in BLACKLIST:
                continue
            module = importlib.import_module(file.strip(".py"))
            self.tools.append(module.tool_export)
            self.function_map[module.tool_export["function"]["name"]] = module.function
            logger.log(
                logging.DEBUG,
                f"DEBUG [ toolchain ]  Registered tool `{module.tool_export["function"]["name"]}`",
            )
