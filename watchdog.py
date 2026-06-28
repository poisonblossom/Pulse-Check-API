#creating a system to register the monitor  
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# store all monitors
monitors = {}

@app.route('/')
def home():
    return "Watchdog is active"

@app.route('/monitors', methods=['POST'])
def register_monitor():

    # Process the JSON sent by the client
    data = request.get_json()

    device_id = data["id"]
    timeout = data["timeout"]
    email = data["alert_email"]

    # Store the monitor
    monitors[device_id] = {
        "timeout": timeout,
        "alert_email": email,
        "last_heartbeat": time.time(),
        "status": "active"
    }

    return jsonify({
        "message": "Monitor created successfully",
        "device": device_id
    }), 201

if __name__ == "__main__":
    app.run(debug=True)