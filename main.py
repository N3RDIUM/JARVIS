import g4f
import json
import math
import utils
from speak import speak
from speech_recognizer import listen_and_save, transcribe

g4f.logging = False # Disable logging
g4f.check_version = False # Disable automatic version checking

dev = False

available_functions = [
    {
        "name": "talk_to_user",
        "returns": None,
        "arguments": [
            {
                "name": "message",
                "type": "string",
                "description": "The message to send to the user."
            }
        ]
    },
    {
        "name": "get_weather",
        "returns": "json",
        "arguments": [
            {
                "name": "location",
                "type": "string",
                "description": "The city to get the weather for."
            }
        ]
    },
    {
        "name": "google_search",
        "returns": "json",
        "arguments": [
            {
                "name": "query",
                "type": "string",
                "description": "The query to search for."
            },
            {
                "name": "n_results",
                "type": "integer",
                "description": "The number of results to return."
            }
        ]
    },
    {
        "name": "calculate",
        "returns": "number",
        "arguments": [
            {
                "name": "expression",
                "type": "string",
                "description": "The expression to evaluate. Note that this will be run in a python shell. You can only use the math module, which is already imported."
            }
        ]
    }
]
def speak_and_print(dict_input):
    message = dict_input["message"]
    if not dev:
        speak(message)
    print(message)
    return None
function_map = {
    "talk_to_user": speak_and_print,
    "get_weather": utils.search_weather,
    "google_search": utils.search_google,
    "calculate": lambda arg_dict: eval(arg_dict["expression"]),
}

messages=[
        {"role": "system", "content": """You are an extremely helpful chatbot.
You can call certain functions in Python by typing the following json format:
{"function_call": "function_name", "arguments": {"argument_name": "argument_value"}}
Here are the functions available to you:

"""+json.dumps(available_functions, indent=4)+"""

Example usage:
User: Hello!
Bot: {"function_call": "talk_to_user", "arguments": {"message": "Hello!"}}
User: What's the weather like in New York?
Bot: {"function_call": "get_weather", "arguments": {"location": "New York"}}
System: function_results: {"weather": "Sunny", "temperature": "72 degrees Fahrenheit"}\nNow tell the user the info that he requested in JSON format!
Bot: {"function_call": "talk_to_user", "arguments": {"message": "The weather in New York is sunny and 72 degrees Fahrenheit."}}

Remember. When calling a function, only include the json object. Do not include the quotes around it, or things like \"To call the function, type\", etc.
"""}]

def evaluate():
    global messages
    while True:
        try:
            # Message will already be in messages
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.1,
                stream=True,
                # provider=g4f.Provider.FreeGpt,
            )
            res = ""
            for message in response:
                print(message, flush=True, end='')
                res += message
            messages += [{"role": "assistant", "content": res}]
            print()
            break
        except Exception as e:
            print(e)
            messages += [{"role": "system", "content": "Error: "+str(e)}]
            return evaluate()
    try:
        res = json.loads(res)
        # Use function_map to call the function
        if "function_call" in res:
            function_name = res["function_call"]
            if function_name in function_map:
                function = function_map[function_name]
                arguments = res["arguments"]
                function_result = function(arguments)
                if function_result != None:
                    messages += [{"role": "system", "content": f"function_results: {json.dumps(function_result)}\nNow tell the user the info that he requested in JSON format!"}]
                    print("function_results: "+json.dumps(function_result))
                    return evaluate()
            else:
                messages += [{"role": "system", "content": "Error: Function "+function_name+" not found"}]
                print("Error: Function "+function_name+" not found")
                return evaluate()
    except json.JSONDecodeError:
        messages += [{"role": "system", "content": "Error: Invalid JSON. Remember, your message can contain only JSON, and nothing else! Try again."}]
        print("Error: Invalid JSON")
        return evaluate()
    return res

while True:
    if not dev:
        print("listening...")
        while True:
            try:
                msg = transcribe(listen_and_save())
                if msg != "": break
            except KeyboardInterrupt: exit()
            except: print("still listening...")
    else: msg = input("> ")
    messages += [{"role": "user", "content": msg}]
    print("User: "+messages[-1]["content"])
    response = evaluate()