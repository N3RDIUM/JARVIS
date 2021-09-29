<h1><img src="https://user-images.githubusercontent.com/74598401/135040774-caf95e55-b70e-4b78-9909-94fb91a0ea98.png"></h1>
<h2>J.A.R.V.I.S is an AI virtual assistant made in python.</h2>

## Running JARVIS

To run JARVIS, make sure you have all the packages by running this code in the command prompt:

    python -m pip install pyaudio speechrecogntion torch playsound pyautogui wolframalpha gtts pywhatkit chatterbot chatterbot-corpus nltk
    
Then, just open a command prompt window inside the repo directory and run:

    python __main__.py
    
To talk to JARVIS, say 'computer' and wait for it to play a sound, and then speak the command.

### Dependencies

JARVIS needs the following packages:

    SpeechRecognition
    PyAudio
    torch
    PlaySound
    PyAutoGUI
    WolframAlpha
    gTTS
    pywhatkit
    chatterbot
    chatterbot-corpus
    nltk
    
## Known Issues
1. The assistant takes too long to respond (will be resolved shortly)
2. It takes some time to respond
3. It doesn't work on devices without python (will be resolved shortly)
4. Some dependencies do not install (will be resolved shortly, by adding a 'DepInstaller.py' file)


