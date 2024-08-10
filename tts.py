import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer, set_seed
import soundfile as sf
import time

device = "cpu"

model = ParlerTTSForConditionalGeneration.from_pretrained(
    "parler-tts/parler-tts-mini-expresso",
).to(device)

pipeline = model.generate
tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-expresso")

prompt = "How am I speaking so fast? It's almost unreal."
description = "Thomaas speaks fast in a, sarcastic low-pitched tone, with emphasis and high quality audio."
prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

t = time.time()
print("Started")

input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
print("Tokenized!")

set_seed(42)
with torch.inference_mode():
    generation = pipeline(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    print("Generation complete!")

sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)
print("Saved to wavfile.")
print(f"Finished in {time.time() - t} seconds.")
