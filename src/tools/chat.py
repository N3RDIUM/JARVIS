tool_export = {
    "type": "function",
    "function": {
        "name": "chat",
        "description": "Chat with the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to send to the user.",
                },
            },
            "required": ["message"],
        },
    },
}


def function(args):
    print(args["message"])
    return {"role": "assistant", "content": args["message"]}
