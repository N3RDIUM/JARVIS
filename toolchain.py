import pyjokes


class Tool:
    def __init__(self, name, description, args):
        self.name = name
        self.description = description
        self.args = args

    def __str__(self):
        return f"Tool: {self.name}\nDescription: {self.description}\nArgs: {self.args}"

    def call(self, **kwargs):
        return {"tool": self.name, "returned": "Nothing"}


class Chat(Tool):
    def __init__(self):
        super().__init__(
            "chat", "Talk to the human", {"message": "Message to send to the human"}
        )

    def call(self, **kwargs):
        print(f"JARVIS: {kwargs['message']}")
        return {
            "tool": self.name,
            "returned": "Success! The message has been delivered to the user.",
        }


class Jokes(Tool):
    def __init__(self):
        super().__init__("jokes", "Get a random joke", {})

    def call(self, **kwargs):
        return {
            "tool": self.name,
            "returned": pyjokes.get_joke() + " Now tell this joke to the user!",
        }


class EndOFTurn(Tool):
    def __init__(self):
        super().__init__(
            "end-of-turn",
            "Use this tool to end your turn of the conversation once you are done responding to the user.",
            {},
        )

    def call(self, **kwargs):
        return {
            "tool": self.name,
            "returned": "Your turn in the conversation has ended, now the user shall act!",
        }


tools = {"chat": Chat(), "jokes": Jokes(), "end-of-turn": EndOFTurn()}
