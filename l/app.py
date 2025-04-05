import win32com.client
import datetime
import webbrowser
import subprocess
import urllib.parse
import pyautogui
import speech_recognition as sr
import threading
from flask import Flask, render_template, jsonify
from llama_client import get_llama_response

app = Flask(__name__)

# Initialize the voice engine
say = win32com.client.Dispatch("SAPI.SpVoice")

# Global state for listening and command history
listening = False
listening_lock = threading.Lock()
commands_history = []
commands_lock = threading.Lock()

def listen_in_background():
    """Continuously listens for commands until stopped."""
    global listening
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 0.8
        print("Listening in background...")

        while True:
            with listening_lock:
                if not listening:
                    print("Stopped listening.")
                    break

            try:
                print("Awaiting command...")
                audio = r.listen(source, timeout=5)
                command = r.recognize_google(audio, language="en-uk")
                print(f"Command received: {command}")
                if command:
                    handle_command(command)
            except sr.WaitTimeoutError:
                print("Listening timed out, waiting for new command...")
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError:
                print("Could not request results; check your network connection.")

def handle_command(command):
    """Processes the received command."""
    global commands_history

    command = command.lower()
    response = ""

    if "time" in command:
        hour = datetime.datetime.now().strftime("%H")
        mi = datetime.datetime.now().strftime("%M")
        response = f"The time is {hour}:{mi}"
        say.Speak(response)

    elif "search" in command:
        search_query = command.split("search")[1].strip()
        if search_query:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
            webbrowser.open(search_url)
            response = f"Searching for {search_query} on Google"
            say.Speak(response)

    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        response = "Opening YouTube"
        say.Speak(response)

    elif "open spotify" in command:
        try:
            subprocess.Popen(["spotify"])
            response = "Opening Spotify"
            say.Speak(response)
        except FileNotFoundError:
            response = "Spotify application not found."
            say.Speak(response)

    elif "open calculator" in command:
        try:
            subprocess.Popen("calc.exe")
            response = "Opening calculator"
            say.Speak(response)
        except FileNotFoundError:
            response = "Calculator application not found."
            say.Speak(response)

    elif "close tab" in command:
        try:
            pyautogui.hotkey("ctrl", "w")
            response = "Closing the current tab."
            say.Speak(response)
        except Exception:
            response = "An error occurred while closing the tab."
            say.Speak(response)

    else:
        # Use LLaMA API for general responses
        response = get_llama_response(command)
        say.Speak(response)

    # Append the command and response to the history
    with commands_lock:
        commands_history.append({"command": command, "response": response})

@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")

@app.route("/start-listening", methods=["GET"])
def start_listening():
    """Starts the voice recognition process in the background."""
    global listening
    with listening_lock:
        if not listening:
            listening = True
            threading.Thread(target=listen_in_background, daemon=True).start()
    return jsonify({"response": "Listening started."})

@app.route("/stop-listening", methods=["GET"])
def stop_listening():
    """Stops the voice recognition process."""
    global listening
    with listening_lock:
        listening = False
    return jsonify({"response": "Listening stopped."})

@app.route("/commands-history", methods=["GET"])
def get_commands_history():
    """Returns the list of commands and responses received so far."""
    with commands_lock:
        return jsonify({"history": commands_history})

if __name__ == "__main__":
    app.run(debug=True)
