import logging
import time
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler("jarvis.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Clear the log file
with open("jarvis.log", "w") as f:
    f.write("")

logger.info("Initializing modules for Local LLM")
from llama_cpp import Llama
import utils
import json

# from speech_recognizer import listen_and_save, transcribe_whisper
from speak import speak

logger.info("Initializing LLM")
quant = "Q5_K_M"
modelpath = f".cache/airoboros-l2-7B-gpt4-2.0.{quant}.gguf"
# TODO: Check if the model exists, if not, download it. Don't just raise an exception
if not os.path.exists(modelpath):
    raise Exception(f"Please downlad the {modelpath.split('/')[-1]} model and keep it in the .cache folder!")
llm = Llama(model_path=modelpath, n_threads=4) # TODO: (for first-time users) Download the model from the internet and enter the path here

# TODO: Make different chat histories and use them for different purposes:
# 1: User interaction
# 2: Research, weather, data collection
# 3: Secondary data collection
# 4: Memory recall and save
# The history purposes will scale with the number of cores available.

curr_state = llm.__getstate__().copy()
print(curr_state)
curr_state["n_ctx"] = 16384
curr_state["temperature"] = 0.1
curr_state["top_p"] = 0.1
llm.__setstate__(curr_state)
curr_state = llm.__getstate__().copy()
print(curr_state)

functions = [
    {
        "name": "chat_with_user", # This function is added because the model hallucinates a lot and calls functions randomly
        "description": "Always use this function to chat with the user instead of returning non-json output.",
        "parameters": [
            {
                "name": "message",
                "description": "The message you want to tell to the user.",
                "type": "string"
            }
        ],
    },
    {
        "name": "get_weather",
        "description": "Use this function to get the weather of a place.",
        "parameters": [
            {
                "name": "location",
                "description": "The location to get the weather of.",
                "type": "string"
            }
        ],
    },
    {
        "name": "search_google",
        "description": "Use this function to search Google. This is like your swiss army knife for acquiring real-world information. If your answer involves real-world information, use this function to search for the required information first. It can also be used to get word meanings, definitions, facts, answers to questions, etc.",
        "parameters": [
            {
                "name": "query",
                "description": "The query to search on Google.",
                "type": "string"
            },
            {
                "name": "n_results",
                "description": "The number of results to return. Minimum is 2, but you can change it to any number you want depending on the use case. If the question you're answering is more broad in nature, you can increase this number. If the question you're answering is more specific in nature, you can decrease this number. Maximum is 16.",
                "type": "int"
            }
        ],
    },
    {
        "name": "do_math",
        "description": "Use this function to do math. It will be executed using Python's eval() function.",
        "parameters": [
            {
                "name": "query",
                "description": "The math expression to solve. It will be executed using Python's eval() function.",
                "type": "string"
            }
        ],
    }
    # TODO: Add more functions!!!!
    # TODO: Add a persistent memory recall and save function
]

def promptify_functions(functions):
    """
    Turn a list of functions into a prompt LLAMA can understand.
    """
    ret = "Available functions:\n"
    for function in functions:
        _new_addition = f"""
{function["name"]}
  description: {function["description"]}
  params:
"""
        for parameter in function["parameters"]:
            _new_addition += f"    {parameter['name']}: {parameter['description']}\n" # TODO: Add dict param support
        ret += _new_addition
    return ret

chat_history = [
        {# TODO: Add each function's description to the system prompt
            "role": "system",
            "content": f"""You are JARVIS, an AI assistant. You are tasked with helping the user with his daily tasks.
You are an AI similar to JARVIS, so make sure you speak like him. Call the user as \'sir\'.
Remember that you WILL NOT use your knowledge for non-conversational tasks, because there is a chance you can hallucinate and give the user wrong information. Instead, you will use the functions provided to you to get the information you need before you respond to the user, whenever necessary.
Here's a list of scenarios where you must use the functions:
- If the user asks you a question that requires real-world information, use the functions provided to search for the information first. This includes definitions, weather, word meanings, etc.
- Never respond like 'as an AI, I dont know/cant do that'. Instead, use the functions provided to you to get the information you need before you respond to the user.

As an AI assistant, please select the most suitable function and parameters from the list of available functions below, based on the user's input. Provide your response in JSON format. Only use the functions which are mentioned below.
{promptify_functions(functions)}
    """
        }
]

# Warm up the LLM
logger.info("Warming up LLM")
out = llm.create_chat_completion(chat_history + [{"role": "system", "content": "Say this is a test!"}], stream=True)
for token in out:
    try:
        print(token["choices"][0]["delta"]["content"], end="", flush=True)
    except KeyError: pass
print()

available_functions = {
    "get_weather": utils.search_weather,
    "search_google": utils.search_google,
    "math": lambda params: {"result": eval(params["query"])},
}
def evaluate_function(function, params):
    """
    Evaluate a function's output for the LLM.
    """
    if function in available_functions:
        return json.dumps(available_functions[function](params))
    else:
        raise NotImplementedError(f"Function {function} not implemented.")
    
def add_to_hist(message, chat_history):
    """
    Add a message to the chat history.
    """
    chat_history.append({
        "role": "function",
        "content": message
    })
    chat_history.append({
        "role": "system",
        "content": "Great! As you can see, the function has returned the output.\nNow, you will take the data you got from this function and respond to the user's query using the chat_with_user function."
    })
    return chat_history
def generate_reply(llm, chat_history):
    final = ""
    generated = 0
    t = time.time()
    output = llm.create_chat_completion(chat_history, stream=True)
    logger.info(f"[LLM] < {chat_history[-1]['content']}")
    _newline = '\n'
    for token in output:
        try:
            delta = token["choices"][0]["delta"]["content"]
            final += delta
            print(f"[Progress: {generated} tokens] {final.replace(_newline, '')}", end="\r", flush=True)
            generated += 1
        except KeyError: pass
    t = time.time() - t
    logger.info(f"[LLM] > Generated {generated} tokens, {len(final)} characters in {t} seconds")
    chat_history.append({ # TODO: Make this func have no side effects
        "role": "assistant",
        "content": final
    })
    # Process function call
    try:
        output = json.loads(final)
        logger.info(f"[LLM] > JSON decoded: {output}")
        if type(output) != dict:
            raise TypeError
        if not "function" in output or not "params" in output:
            raise KeyError
        if output["function"] == "chat_with_user":
            logger.info(f"[LLM] > !TO:USER > {output['params']['message']}")
            print(f"A: {output['params']['message']}")
            # speak(output['params']['message'])
        else:
            try:
                logger.info(f"[LLM] > !TO:FUNCTION > {output['function']}({output['params']})")
                function_output = evaluate_function(output["function"], output["params"])
                logger.info(f"[FUNCTION] > {function_output}")
                chat_history = add_to_hist(function_output, chat_history)
                logger.info(f"[LLM] < Generating reply for function output")
                generate_reply(llm, chat_history)
            except NotImplementedError:
                logger.info(f"[LLM] > Function not implemented. Prompting to use one of the available functions!")
                chat_history.append({
                    "role": "system",
                    "content": "Sorry, the function you requested is not implemented. Please try one of: " + ", ".join([function["name"] for function in functions]) + "."
                })
                generate_reply(llm, chat_history)
    except json.decoder.JSONDecodeError:
        logger.info(f"[LLM] > JSON decode error. Prompting to use JSON only!")
        chat_history.append({
            "role": "system",
            "content": "That output is not valid JSON. Please try again."
        })
        generate_reply(llm, chat_history)
    except TypeError:
        logger.info(f"[LLM] > JSON decode error. Prompting to use JSON only!")
        chat_history.append({
            "role": "system",
            "content": "That output is not valid JSON. Please try again."
        })
        generate_reply(llm, chat_history)

while True:
    user_query = input("Q: ")
    # listen_and_save()
    # user_query = transcribe_whisper()
    if user_query and user_query != "":
        chat_history.append({
            "role": "user",
            "content": user_query
        })
        generate_reply(llm, chat_history)
