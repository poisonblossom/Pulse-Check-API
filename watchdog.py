# creating a system to register the monitor  
from flask import Flask, request, jsonify
import threading 
import time


app = Flask(__name__)

# store all monitors
monitors = {}

lock = threading.Lock()


@app.route('/')
def home():
    return "Watchdog is active"


@app.route('/monitors', methods=['POST'])
def register_monitor():

    # process the JSON sent by the client
    data = request.get_json()

    device_id = data["id"]
    timeout = data["timeout"]
    email = data["alert_email"]

    with lock:
        # Store the monitor
        monitors[device_id] = {
            "timeout": timeout,
            "alert_email": email,
            "last_heartbeat": time.time(),
            "status": "active",
            "paused": False
        }

    return jsonify({
        "message": "Monitor created, weldone",
        "device": device_id
    }), 201


# check for the monitor and start the countdown 
@app.route('/monitors/<device_id>/heartbeat', methods=['POST'])
def heartbeat(device_id):
    with lock:
        if device_id not in monitors:
            return jsonify({"error": "Monitor not found"}), 404

        monitor = monitors[device_id]

        # reset the timer 
        monitor["last_heartbeat"] = time.time()
        monitor["status"] = "active"

    return jsonify({"message": "Heartbeat received", "device": device_id}), 200


# pause monitoring
@app.route('/monitors/<device_id>/pause', methods=['POST'])
def pause_monitor(device_id):
    with lock:
        if device_id not in monitors: 
            return jsonify({"error": "Monitor not found"}), 404

        monitors[device_id]["paused"] = True

    return jsonify({"message": "Monitoring paused", "device": device_id}), 200


# view all registered monitors
@app.route('/monitors', methods=['GET'])
def view_monitors():
    with lock:
        return jsonify(monitors.copy())


# watchdog alert time 
def watchdog():
    while True:
        time.sleep(1)

        with lock: 
            current_time = time.time()
            items = list(monitors.items())

            for device_id, monitor in items:

                if monitor["paused"]:
                    continue

                elapsed = current_time - monitor["last_heartbeat"]

                if elapsed >= monitor["timeout"]:
                    if monitor["status"] == "active":
                        print({
                            "ALERT": f"Device {device_id} is down",
                            "time": time.time()
                        })
                        monitor["status"] = "down"


if __name__ == "__main__":
    thread = threading.Thread(target=watchdog, daemon=True)
    thread.start()

    app.run(debug=True, use_reloader=False)