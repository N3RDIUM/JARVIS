import logging

import ollama

import inputs
import tools
from logger import logger

logger.log(logging.DEBUG, "DEBUG [ main      ]  Nothing.")

toolchain = tools.Toolchain()
input_man = inputs.InputManager()

toolchain.register_tools()
input_man.register_inputs()
input_man.begin_streams()

# Mainloop
client = ollama.Client()
model = "nemotron-mini"
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant who gives short, concise responses.",
    },
]
while True:
    messages.append({"role": "user", "content": input("> ")})
    response = client.chat(model=model, messages=messages, tools=toolchain.tools)
    print(f"< {response}")
    messages.append(response["message"])

    if not response["message"].get("tool_calls"):
        # messages.append(
        #     {
        #         "role": "system",
        #         "content": "Oops! Please use tools to respond, not plain text!",
        #     }
        # )
        continue

    for call in response["message"]["tool_calls"]:
        tool_response = toolchain.eval_call(call)
        if tool_response is None:
            continue
        messages.append(tool_response)

input_man.kill_streams()
