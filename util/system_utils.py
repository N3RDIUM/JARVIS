# imports
import os

# nothing special here
def shutdown():
    os.system('shutdown /s /t 1')

def restart():
    os.system('shutdown /r /t 1')

def logoff():
    os.system('shutdown /l /t 1')

def launch_python():
    os.system('python')
