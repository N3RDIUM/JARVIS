from chat import ChatModel

model = ChatModel()
print(model.messages[0]["content"])
while True:
    query = input("> ")
    model.chat(query)
