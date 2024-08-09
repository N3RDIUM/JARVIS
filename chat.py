import ollama
import json
from toolchain import tools


class ChatModel:
    def __init__(self):
        self.messages = [self.build_system_prompt()]

    def add(self, message):
        self.messages.append(message)

    def chat(self, query):  # TODO! Remake this
        self.add({"role": "user", "content": query})
        while True:
            msg = ollama.chat(model="gemma2:2b", messages=self.messages, stream=True)
            response = ""
            for token in msg:
                print(token["message"]["content"], end="", flush=True)
                response += token["message"]["content"]

            response = (
                response.strip().removeprefix("```json").removesuffix("```").strip()
            )
            print()
            try:
                response = json.loads(response)
                self.add({"role": "assistant", "content": json.dumps(response)})
            except json.decoder.JSONDecodeError:
                self.add(
                    {
                        "role": "system",
                        "content": "The JSON you entered is invalid and could not be parsed. Please respond with valid JSON content.",
                    }
                )
                print(self.messages[-1]["content"])
                continue

            try:
                if response["call"] == "end-of-turn":
                    break
            except KeyError:
                self.add(
                    {
                        "role": "system",
                        "content": "Please respond with a valid tool call. The format is: {'call': 'tool-name', 'args': {'argname': 'value'}}",
                    }
                )
                print(self.messages[-1]["content"])
                continue

            try:
                tool = tools[response["call"]].call
            except KeyError:
                self.add(
                    {
                        "role": "system",
                        "content": "The tool you entered is invalid. Please respond with a valid tool name. Tools are case sensitive! The available tools are: "
                        + ", ".join(tools.keys()),
                    }
                )
                print(self.messages[-1]["content"])
                continue

            args = {}
            if "args" in response:
                args = response["args"]
                args = {k: v for k, v in args.items() if v is not None}

            try:
                res = tool(**args)
            except Exception as e:
                self.add(
                    {
                        "role": "system",
                        "content": f"The tool you entered is valid, but it threw an error. The error was: {e}",
                    }
                )
                print(self.messages[-1]["content"])
                continue
            self.add(
                {
                    "role": "system",
                    "content": json.dumps(res)
                    + "\n\n"
                    + "Now, what would you like to do? (Use the tool 'end-of-turn' to end your turn in the conversation)",
                }
            )
            print(json.dumps(res))
            if res["tool"] == "end-of-turn":
                break

        return self.messages

    def build_tool_prompt(self, tool_name):
        return str(tools[tool_name])

    def all_tool_prompts(self):
        ret = ""
        for tool in tools:
            ret += self.build_tool_prompt(tool) + "\n\n"
        return ret

    def build_system_prompt(self):
        return {  # TODO! Remake the prompt
            "role": "system",
            "content": f"""You are a helpful assistant. You always JSON tools and never speak in plaintext.
Tool usage format (beware, it is case sensitive): {json.dumps({'call': 'tool-name', 'args': {'argname': 'value'}})}
Please use the 'end-of-turn' tool to finish your turn in the conversation.

Here is some information about the available tools:
[TOOL LIST STARTS]

{self.all_tool_prompts()}[TOOL LIST ENDS]

Remember, you are encouraged to not give negative responses and responses that portray your lack of knowledge.
So, use these tools to generate your response wherever required.
You will use only one tool per response, else you will be penalised.
Never reply in plain text. Always use tools to respond.
Your ENTIRE response will be parsed as JSON using python's json library, make sure you respond with valid JSON.
You cannot put ANYTHING outside the {{}}s, and no backticks.
You CANNOT place multiple tool calls in a single message separated by a newline. Don't worry, you WILL get a chance
to call another tool before the user acts. You have the power to call the `end-of-turn` tool, after all.

Let the conversation begin!
""",
        }
