# NOTE: To use gpt-4 in LocalAI, download a model of your choice from huggingface (preferably airoboros-l2-7b-gpt4-2.0.ggmlv3.q4_0.bin)
# NOTE: Then place it in the models folder
# NOTE: Then, add a yaml file with the same name as the model in the models folder and add the following (without the #, of course, and replace the model name with the name of your model):

# name: gpt-4
# parameters:
#   model: airoboros-l2-7b-gpt4-2.0.ggmlv3.q4_0.bin
#   top_p: 80
#   top_k: 0.9
#   temperature: 0.1
# backend: "llama" # Set the `llama` backend

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler("jarvis.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Initializing modules for Local LLM functions")
import os
import openai
openai.api_base = "http://localhost:8080/v1"
openai.api_key = "sx-xxx"
OPENAI_API_KEY = "sx-xxx"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

import json
import random
logger.info("Modules initialized.")

def confid_and_reason(kwargs):
    return kwargs["confidence"], kwargs["reason"]

def get_current_weather(location, unit="fahrenheit", **kwargs):
    """Get the current weather in a given location"""
    confidence, reason = confid_and_reason(kwargs)
    logger.info(f"[FUNCTION] > get_current_weather called with location={location}, unit={unit}, confidence={confidence}, reason={reason}")
    weather_info = {
        "location": location,
        "temperature": random.randint(50, 100),
        "unit": unit,
        "forecast": random.choice(["sunny", "windy"]),
    }
    logger.info(f"[FUNCTION] < get_current_weather returned {json.dumps(weather_info)}")
    return json.dumps(weather_info)

messages = [
    {"role": "system", "content": "You are a conversational AI assistant that follows instruction extremely well. Help as much as you can. Give concise and helpful answers. Be polite and respectful at all times. Call the user as \"Sir\". Only call functions when there is a valid reason. Only call the given functions."},
]

def run_conversation(query):
    # Step 1: send the conversation and available functions to GPT
    global messages
    messages.append({"role": "user", "content": query})
    functions = [
        {
            "name": "get_current_weather",
            "description": "Returns the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    "confidence": {
                        "type": "number",
                        "description": "The confidence level of why you think the user wants to know the weather, from 0 to 1 in decimal form",
                    },
                    "reason": {
                        "type": "string",
                        "description": "The reason why you think the user wants to know the weather.",
                    },
                },
                "required": ["location", "confidence", "reason"],
            },
        }
    ]
    logger.info(f"[GPT] > Starting Chain for response to: {query}")
    # print(messages)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.1,
    )
    # print(response)
    response_message = response["choices"][0]["message"]
    logger.info(f"[GPT] < Response: {response_message}")
    if not response_message.get("function_call"):
        # Step 2: if GPT didn't want to call a function, just return its response
        messages.append({"role": "assistant", "content": response_message["content"]})
        return response_message["content"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(**function_args)

        # Step 4: send the info on the function call and function response to GPT
        messages.extend([
            {
                "role": "function",
                "name": str(function_name),
                "content": str(function_response),
            },
            {
                "role": "system",
                "content": "Great! As you can see, the function returned to you a JSON object containing the data the user wants, but the user does not understand JSON. Now, you may extract the information you need from the JSON object and return it to the user in English. Remember to be clear and concise and respond according to the conversation.",
            }
        ])
        # print(messages[-2])
        logger.info(f"[GPT] > Chain: Converting {messages[-2]['content']} to English using GPT")
        second_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.0,
        )  # get a new response from GPT where it can see the function response
        logger.info(f"[GPT] < Response: {second_response['choices'][0]['message']['content']}")
        # print(second_response)
        messages.append({"role": "assistant", "content": second_response["choices"][0]["message"]["content"]})
        return r"{}".format(second_response["choices"][0]["message"]["content"].replace("Assistant: ", ""))

while True:
    query = input("> ")
    # query = "What is the weather in San Francisco?"
    response = run_conversation(query)
    print(response)