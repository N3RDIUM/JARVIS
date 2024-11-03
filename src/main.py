import logging

import inputs
import tools
from logger import logger

logger.log(logging.DEBUG, "DEBUG [ main      ]  Nothing.")

toolchain = tools.Toolchain()
input_man = inputs.InputManager()

toolchain.register_tools()
input_man.register_inputs()
input_man.begin_streams()
