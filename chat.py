import threading
import ollama
import json
import time

# TODO: Move to constants.py
# Model status constants
IDLE = 0
THINKING = 1
EVALUATING = 2

# Generation constnats
NOTHING = '{"status": "idle"}'


def string_is_json(string: str):
    try:
        json.loads(string)
    except json.JSONDecodeError:
        return False
    except ValueError:
        return False
    return True


SYSTEM_PROMPT = f"""You are a helpful assistant who gives short and concise answers without emojis.
Always respond with JSON in the following format: {{"message": "your-text-here"}}

You may be called upon even when you don't have anything to do.
Being the super-intelligent AI you are, you will identify silently whether you have any work to do.
If you do, you are free to do so in the usual way. Else, if you don't have any work, you may respond
with {NOTHING} and call it a day.
"""

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
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
                options={"temperature": 0.0},
                format="json",
            )["message"]
            self.model_status = EVALUATING
            self.evaluate_message(message)
            self.model_status = IDLE

    def evaluate_message(self, message):
        content = message["content"]
        print(content)

        if NOTHING in content:
            print("Waiting...")
            return

        if not string_is_json(content):
            self.add_message(message)
            self.add_message(
                {
                    "role": "system",
                    "content": f"The JSON you provided is invalid. \
Please try again with the corrected JSON synyax \
for the same: {content}.",
                }
            )
            return

        self.messages.append({"role": "assistant", "content": content})


model = ChatModel()
while True:
    model.user_input(input(">"))
