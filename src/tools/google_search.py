tool_export = {
    "type": "function",
    "function": {
        "name": "google_search",
        "description": "Search google for anything!",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to be searched on google.",
                },
            },
            "required": ["message"],
        },
    },
}

function = print  # TODO
