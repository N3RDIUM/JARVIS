import sys
from cx_Freeze import setup, Executable

build_exe_options = {"includes": ["chatterbot", "speech_recognition",
                                  "pyaudio", "gtts", "chatterbot_corpus", "torch", "nltk", "pywhatkit", "srsly", "cymem", "blis", "_soundfile_data", "en_web_core_sm"]}

setup(
    name="JARVIS",
    version="0.0.2",
    description="JARVIS is an AI virtual assistant.",
    options={"build_exe": build_exe_options},
    executables=[Executable("__main__.py")])
