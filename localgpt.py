from gpt4all import GPT4All
# from speech_recognizer import listen_and_save, transcribe_whisper

# models = GPT4All.list_models()
# for model in models:
#     print(model)

model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin", device="cpu", n_threads=6, model_path=".cache/")

system_prompt = f"""
You are a decision-making chatbot. You must respond to queries with a number according to the following rules:
1. If the user is involved in general conversation, you must respond with 0.
2. If the user is asking for a joke, you must respond with 1.
"""
# print(system_prompt)

with model.chat_session(system_prompt):
    while True:
        # listen_and_save()
        # transcribed = f"{transcribe_whisper()}".strip()
        transcribed = input("[YOU]: ")
        _response = model.generate(prompt=transcribed, temp=0, streaming=True)
        for response in _response:
            print(response, end="")
        print()