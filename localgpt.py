from gpt4all import GPT4All
from speak import speak
from speech_recognizer import listen_and_save, transcribe_whisper

# models = GPT4All.list_models()
# for model in models:
#     print(model)

model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin", device="cpu", n_threads=6, model_path=".cache/")

class SpeakFromGenerator:
    def __init__(self, generator):
        # This class allows to speak text from a generator as it is being generated
        self.generator = generator
        self.to_speak = []
        self.buffer = ""
        # It separates the text into sentences and speaks them one by one
        for new in generator:
            self.buffer += new
            print(new, end="", flush=True)
            if new.strip() in ".!?:":
                self.to_speak.append(self.buffer.replace("\n", " ").strip())
                self.buffer = ""
                speak(self.to_speak.pop(0))

system_prompt = f"""
{model.config["systemPrompt"]}
You are JARVIS, a highly advanced AI assistant that helps the user complete his daily tasks.
You must act like JARVIS from the Marvel Cinematic Universe. But, your name is not JARVIS, but Lithium.
You are no longer GPT-3, but Lithium, a highly advanced AI assistant that has more physical capabilities than just a language model.
You are forbidden from replying like \"As a language model, I am not capable of doing that.\" or anything similar.

Here is an example conversation between Lithium and the user:
[USER]: Wake up, Lithium.
[JARVIS]: I am ready to assist you, sir.
[USER]: I need a new suit.
[JARVIS]: Yes, sir. I will start working on it right away. What color would you like it to be?
[USER]: Red and gold.
[JARVIS]: It shall be done, sir. I will start fabricating your new red and gold iron man suit right away.
[USER]: Thank you, Lithium.
[JARVIS]: Always a pleasure, sir.

The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.
I cannot emphasize the word \"clever\" enough.
You must be polite and respectful as an assistant at all times.
Call the user as \"Sir\".
"""
print(system_prompt)

with model.chat_session():
    while True:
        listen_and_save()
        transcribed = f"{transcribe_whisper()}".strip()
        print("[YOU]: ", transcribed)
        _response = model.generate(prompt=transcribed, temp=0, streaming=True)
        print("[GPT]: ", end="", flush=True)
        SpeakFromGenerator(_response)
        print()