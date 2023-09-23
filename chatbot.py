import logging
import time
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

logger.info("Initializing LLM")
llm = Llama(model_path=".cache/airoboros-l2-7B-gpt4-2.0.Q4_0.gguf")
curr_state = llm.__getstate__()
print(curr_state)
curr_state["n_ctx"] = 32786
curr_state["temperature"] = 0.1
llm.__setstate__(curr_state)

functions = [
    {
        "name": "chat_with_user", # This function is added because the model hallucinates a lot and calls functions randomly
        "description": "Use this function to add a message to the chat history to tell the user. Do not respond without JSON output. If you dont want to call any other function and just want to speak to the user, just call this function.",
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
        "description": "Use this function to search Google. This is like your swiss army knife for acquiring real-world information. If your answer involves real-world information, use this function to search for the required information first.",
        "parameters": [
            {
                "name": "query",
                "description": "The query to search on Google.",
                "type": "string"
            },
            {
                "name": "n_results",
                "description": "The number of results to return. Default is 4, but you can change it to any number you want depending on the use case. If the question you're answering is more broad in nature, you can increase this number. If the question you're answering is more specific in nature, you can decrease this number. Minimum is 1, maximum is 16.",
                "type": "int"
            }
        ],
    }
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

available_functions = {
    "get_weather": utils.search_weather,
    "search_google": utils.search_google
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
        "content": "Great! As you can see, the function has returned the output. Please use the chat_with_user function to tell the user the data he wants from the data you got from this function!"
    })
    return chat_history
def generate_reply(llm, chat_history):
    final = ""
    generated = 0
    t = time.time()
    output = llm.create_chat_completion(chat_history, stream=True)
    logger.info(f"[LLM] < {chat_history[-1]['content']}")
    for token in output:
        try:
            delta = token["choices"][0]["delta"]["content"]
            final += delta
            print(f"Progress: {generated} tokens", end="\r", flush=True)
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
        if not "function" in output or not "params" in output:
            raise KeyError
        if output["function"] == "chat_with_user":
            logger.info(f"[LLM] > !TO:USER > {output['params']['message']}")
            print(f"A: {output['params']['message']}")
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
            "content": "That output is not valid JSON. Please try again. Remember to use the chat_with_user function to chat with the user!"
        })
        generate_reply(llm, chat_history)

while True:
    # NOTE: Currently, the bot will forget previous chat history. I'm working on a memory system for this, because I dont want to fill up the context size with chat history.
    chat_history = [
        {# TODO: Add each function's description to the system prompt
            "role": "system",
            "content": f"""As an AI assistant, please select the most suitable function and parameters from the list of available functions below, based on the user's input. Provide your response in JSON format. Only use the functions which are mentioned below.
    {promptify_functions(functions)}
    """
        }
    ]
    user_query = input("Q: ") + " [Remember to respond with JSON function calls only, and use only the functions which are given to you!]"
    chat_history.append({
        "role": "user",
        "content": user_query
    })
    generate_reply(llm, chat_history)