import threading
import ollama
import json
# import time

SYSTEM_PROMPT = f"""You are a super-intelligent AI who gives short and concise answers without emojis.
You never speak in plain text, and interact instead using tool calls. 
Tools let you do everything, from speaking to the user to retrieving data.
Here's an example tool call: {r"""{
    tool_name: "example",
    args: {
        foo: "bar",
    }
}"""}

The available tools are:
{r"""[
    {
        name: 'idle',
        description: 'do nothing',
        args: none
    },
    {
        name: 'chat',
        description: 'talk to the human',
        args: {
            message: {
                type: 'string',
                description: 'your search query here'
            }
        }
    },
    {
        name: 'time',
        description: 'get the current time',
        args: none
    },
]"""}

You may be called upon even when you don't have anything to do.
Being the super-intelligent AI you are, you will identify silently whether you have any work to do.
If you do, you are free to do so in the usual way.
If there is no work to be done, call the 'idle' tool.
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
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "I understand. How may I help you?"},
        ]
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
            # time.sleep(1 / 42)  # TODO: Make this configurable using settings.json
            message = ollama.chat(
                model="gemma2:2b",  # TODO: Make this configurable using settings.json
                messages=self.messages,
                options={"temperature": 0.0},
                format="json",
            )["message"]
            self.evaluate_message(message)

    def evaluate_message(self, message):
        content = message["content"]

        self.messages.append({"role": "assistant", "content": content})
        print(f"< {content}")

    def kill(self):
        self.thread.join()
