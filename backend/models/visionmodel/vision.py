

import time
import threading
from collections import deque
import cv2
import numpy as np
import requests
import torch
from ultralytics import YOLO

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8m.pt"
VIDEO_PATH = "video1.mp4"
OUTPUT_PATH = "output_proof_video_ui.avi"
SERVER_URL = "http://127.0.0.1:8000/metrics"
POST_INTERVAL = 1.0

VEHICLE_CLASSES = {"car", "bus", "truck", "motorcycle", "motorbike"}
GRID_SIZE = (8, 8)
SMOOTH_WINDOW = 8
CONF_THRESH = 0.3
MIN_BOX_SIZE = 25
FRAME_RESIZE = 720
FRAME_SKIP = 1

# ---------------- LOAD YOLO ----------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {device.upper()}")
model = YOLO(MODEL_PATH)
model.to(device)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Error opening video: {VIDEO_PATH}")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("Empty video / cannot read first frame")

H0, W0 = frame.shape[:2]
scale = FRAME_RESIZE / H0
W, H = int(W0 * scale), FRAME_RESIZE
grid_h, grid_w = GRID_SIZE
cell_h, cell_w = H // grid_h, W // grid_w

history = deque(maxlen=SMOOTH_WINDOW)
last_post_time = 0.0

# Video writer for proof
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (W, H))

vehicles_per_frame = []

# ---------------- UTILITIES ----------------
def post_metrics_async(payload):
    """Send metrics without blocking main loop."""
    def send():
        try:
            requests.post(SERVER_URL, json=payload, timeout=0.5)
        except:
            pass
    threading.Thread(target=send, daemon=True).start()

# ---------------- PROCESS VIDEO ----------------
frame_idx = 0
fps_deque = deque(maxlen=10)
last_valid_frame = None  # store last valid frame

print("[INFO] Starting video analysis. Press ESC to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    last_valid_frame = frame.copy()  # keep last frame for final overlay
    frame_idx += 1

    # Print frame progress every 50 frames
    if frame_idx % 50 == 0:
        print(f"[INFO] Processed {frame_idx} frames...")

    if FRAME_SKIP and frame_idx % (FRAME_SKIP + 1) != 0:
        continue

    t0 = time.time()
    frame = cv2.resize(frame, (W, H))
    results = model(frame, conf=CONF_THRESH, verbose=False, device=device)[0]

    vehicle_mask = np.zeros((grid_h, grid_w), dtype=np.float32)
    vehicle_count = 0
    approach_counts = {"N": 0, "E": 0, "S": 0, "W": 0}

    for box in results.boxes:
        try:
            cls = int(box.cls[0])
        except:
            cls = int(box.cls)
        label = model.names.get(cls, str(cls)).lower()
        if label not in VEHICLE_CLASSES:
            continue

        coords = box.xyxy[0] if hasattr(box.xyxy, "__len__") else box.xyxy
        x1, y1, x2, y2 = map(int, coords)
        w, h = x2 - x1, y2 - y1
        if w < MIN_BOX_SIZE or h < MIN_BOX_SIZE:
            continue

        vehicle_count += 1
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 180, 0), 2)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

        r1, r2 = max(0, y1 // cell_h), min(grid_h - 1, y2 // cell_h)
        c1, c2 = max(0, x1 // cell_w), min(grid_w - 1, x2 // cell_w)
        vehicle_mask[r1:r2+1, c1:c2+1] = 1.0

        if cy < H // 2:
            approach_counts["N"] += 1
        else:
            approach_counts["S"] += 1
        if cx < W // 2:
            approach_counts["W"] += 1
        else:
            approach_counts["E"] += 1

    # ---------------- CONGESTION METRIC ----------------
    coverage = vehicle_mask.mean() * 100.0
    metric = 0.6 * coverage + 0.4 * min(vehicle_count * 3, 100)
    history.append(metric)
    smooth_metric = float(np.mean(history))

    if smooth_metric < 25:
        status, color = "Light Traffic", (0, 255, 0)
    elif smooth_metric < 55:
        status, color = "Moderate Traffic", (0, 255, 255)
    else:
        status, color = "Heavy Traffic", (0, 0, 255)

    vehicles_per_frame.append(vehicle_count)
    fps = 1 / (time.time() - t0 + 1e-6)
    fps_deque.append(fps)
    avg_fps = np.mean(fps_deque)

    # ---------------- OVERLAY LIVE INFO ----------------
    cv2.putText(frame, f"Vehicles: {vehicle_count}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Congestion: {status} ({smooth_metric:.1f}%)", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"N:{approach_counts['N']} E:{approach_counts['E']}", (10, H - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2)
    cv2.putText(frame, f"S:{approach_counts['S']} W:{approach_counts['W']}", (10, H - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2)
    cv2.putText(frame, f"{avg_fps:.1f} FPS", (W - 160, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Smart Traffic Congestion", frame)
    out.write(frame)

    # POST METRICS ASYNC
    now = time.time()
    if now - last_post_time >= POST_INTERVAL:
        payload = {
            "timestamp": now,
            "counts": approach_counts,
            "overall_congestion": float(smooth_metric),
        }
        post_metrics_async(payload)
        last_post_time = now

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

# ------------------------------- FINAL SIGNAL OPTIMIZATION -------------------------------
avg_vehicles = sum(vehicles_per_frame) / len(vehicles_per_frame)
max_vehicles = max(vehicles_per_frame) if max(vehicles_per_frame) > 0 else 1
avg_congestion = (avg_vehicles / max_vehicles) * 100

def congestion_level(avg_congestion):
    if avg_congestion < 40:
        return "Light"
    elif avg_congestion < 70:
        return "Moderate"
    else:
        return "Heavy"

def optimize_signal(original_time, avg_congestion):
    return round(original_time * (1 + (avg_congestion - 50)/100), 2)

original_time = 28.0
optimized_time = optimize_signal(original_time, avg_congestion)
level = congestion_level(avg_congestion)
time_diff = round(optimized_time - original_time, 2)

# ------------------------------- FINAL OVERLAY -------------------------------
final_frame = last_valid_frame.copy()  # use last valid frame
text_lines = [
    f"Average vehicles/frame: {avg_vehicles:.1f}",
    f"Avg congestion: {avg_congestion:.1f}% -> {level}",
    f"Original signal: {original_time}s",
    f"Optimized signal: {optimized_time}s (+{time_diff}s)"
]

y0, dy = 50, 50
for i, line in enumerate(text_lines):
    y = y0 + i*dy
    cv2.putText(final_frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

cv2.imshow("Final Traffic Analysis", final_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("\n========== FINAL RECOMMENDATION ==========")
print(f"Average vehicles/frame: {avg_vehicles:.1f}")
print(f"Avg congestion: {avg_congestion:.1f}% -> {level}")
print(f"Original (inferred): {original_time}s | Optimized: {optimized_time}s (+{time_diff}s)")
print("==========================================")
print(f"[INFO] Proof video saved at: {OUTPUT_PATH}")
