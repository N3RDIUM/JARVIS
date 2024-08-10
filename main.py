from chat import ChatModel

model = ChatModel()
while True:
    try:
        model.user_input(input("> "))
    except KeyboardInterrupt:
        print("Interrupted.")
        break
model.kill()
