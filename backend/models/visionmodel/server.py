# server.py
from flask import Flask, request, jsonify
from collections import deque
import time
import threading

app = Flask(__name__)

# keep short history for smoothing (last 60 seconds)
history = deque(maxlen=60)

@app.route("/metrics", methods=["POST"])
def metrics():
    payload = request.get_json()
    # expected keys: {"timestamp":..., "counts": {"N":int,...}, "overall_congestion": float}
    payload.setdefault("received_at", time.time())
    history.append(payload)
    return jsonify({"status":"ok"})

@app.route("/latest", methods=["GET"])
def latest():
    if not history:
        return jsonify({"error": "no data"}), 404
    return jsonify(history[-1])

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(list(history))

if __name__ == "__main__":
    app.run(port=5000)
