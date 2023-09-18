import os
import openai
openai.api_base = "http://localhost:8080/v1"
openai.api_key = "sx-xxx"
OPENAI_API_KEY = "sx-xxx"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

import json
import pyjokes
import random

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": random.randint(50, 100),
        "unit": unit,
        "forecast": random.choice(["sunny", "windy"]),
    }
    return json.dumps(weather_info)
def get_joke():
    return pyjokes.get_joke()

messages = [
    {"role": "system", "content": "You are an AI assistant that follows instruction extremely well. Help as much as you can. Give concise and helpful answers. Be polite and respectful at all times. Call the user as \"Sir\"."},
]

def run_conversation(query):
    # Step 1: send the conversation and available functions to GPT
    global messages
    messages.append({"role": "user", "content": query})
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]

    # print(messages)
    response = openai.ChatCompletion.create(
        model="llama-2-7b-chat.ggmlv3.q4_0.bin",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.7,
    )
    print(response)
    response_message = response["choices"][0]["message"]
    if not response_message.get("function_call"):
        # Step 2: if GPT didn't want to call a function, just return its response
        messages.append({"role": "assistant", "content": response_message["content"]})
        return response_message["content"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_joke": get_joke,
            "get_current_weather": get_current_weather
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(**function_args)

        # Step 4: send the info on the function call and function response to GPT
        messages.append(
            {
                "role": "function",
                "name": str(function_name),
                "content": str(function_response),
            }
        )
        second_response = openai.ChatCompletion.create(
            model="llama-2-7b-chat.ggmlv3.q4_0.bin",
            messages=messages,
            temperature=0.7,
        )  # get a new response from GPT where it can see the function response
        print(second_response)
        messages.append({"role": "assistant", "content": second_response["choices"][0]["message"]["content"]})
        return r"{}".format(second_response["choices"][0]["message"]["content"].replace("Assistant: ", ""))

while True:
    query = input("> ")
    response = run_conversation(query)
    print(response)