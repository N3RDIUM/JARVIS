import os
import openai
import random
openai.api_base = "http://localhost:8080/v1"
openai.api_key = "sx-xxx"
OPENAI_API_KEY = "sx-xxx"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

import json

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": random.randint(50, 100),
        "unit": unit,
        "forecast": random.choice(["sunny", "windy"]),
    }
    return json.dumps(weather_info)

def run_conversation(query):
    # Step 1: send the conversation and available functions to GPT
    messages = [
        {"role": "system", "content": "You are the helpful assistant who responds to every query of the user. Please call functions ONLY when necessary, and not for every query."},
        {"role": "user", "content": query},
    ]
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location only when the user asks for it. This function should only be called when the user asks for weather at a particular location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The name of the location to get the weather for.",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="orca-mini-3b.ggmlv3.q4_0.bin",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
        max_tokens=64,
    )
    print(response)
    response_message = response["choices"][0]["message"]
    if not response_message.get("function_call"):
        # Step 2: if GPT didn't want to call a function, just return its response
        return response_message["content"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.extend([
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        ])
        second_response = openai.ChatCompletion.create(
            model="orca-mini-3b.ggmlv3.q4_0.bin",
            messages=messages,
            temperature=0.7,
            max_tokens=128
        )  # get a new response from GPT where it can see the function response
        print(second_response)
        return r"{}".format(second_response["choices"][0]["message"]["content"].replace("Assistant: ", ""))

while True:
    query = input("> ")
    response = run_conversation(query)
    print(response)