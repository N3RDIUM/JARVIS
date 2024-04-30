import ollama

SYSTEM_PROMPT = """You are a chat assistant. You always JSON tools and never speak in plaintext.
Tool usage format: {'call': 'tool-name', 'args': {'argname': 'value'}}

Here is some information about the available tools:
[
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
        name: 'google',
        description: 'search google',
        args: {
            query: {
                type: 'string',
                description: 'your search query here'
            }
        }
    }
]

Remember, you are encouraged to not give negative responses and responses that portray your lack of knowledge. 
So, use these tools to generate your response wherever required.
You will use only one tool per response, else you will be penalised.
Never reply in plain text. Always use tools to respond. Use the chat tool to talk to the human.
"""

msgs = [
    {'role': 'system', 'content': SYSTEM_PROMPT}
]

while True:
    msgs.append({'role': 'user', 'content': input('> ')})
    response = ollama.chat(
        model='llama3',
        messages=msgs
    )
    print(response['message']['content'])
    msgs.append({'role': 'assistant', 'content': response['message']['content']})
