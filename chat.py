import threading
import ollama
import json
import time

# Model status constants
# TODO: Move to constants.py
IDLE = 0
THINKING = 1
EVALUATING = 2


def string_is_json(string: str):
    try:
        json.loads(string)
    except json.JSONDecodeError:
        return False
    except ValueError:
        return False
    return True


# Handling newlines
# Only consider the first line so thet you don't have
# to deal with the multiple-tool-call stuff.
# In the chat function, have the model use <|newline|>
# and replace this token with \n later.


class ChatModel:
    """
    Event-based looping llm thing
    Read the code and you'll understand what I mean.
    """

    def __init__(self) -> None:
        self.messages = []
        self.model_status = IDLE
        self.thread = threading.Thread(
            target=self.start_thread,
        )
        self.thread.start()

    def add_message(self, message) -> None:
        self.messages.append(message)

    def user_input(self, text):
        self.messages.append({"role": "user", "content": text})

    def start_thread(self):
        while True:
            time.sleep(0.42)  # TODO: Make this configurable using settings.json
            self.model_status = THINKING
            message = ollama.chat(
                model="gemma2:2b",  # TODO: Make this configurable using settings.json
                messages=self.messages,
            )
            self.model_status = EVALUATING
            self.evaluate_message(message)
            self.model_status = IDLE

    def evaluate_message(self, message):
        if "<|^-^|>" in message["content"]:
            return
        if not string_is_json(message["content"]):
            self.add_message(message)
            self.add_message(
                {
                    "role": "system",
                    "content": f"The JSON you provided is invalid. \
                        Please try again with the corrected JSON synyax \
                        for the same: {message["content"]}.",
                }
            )
