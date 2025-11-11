
import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8m.pt"
VIDEO_PATH = "Video.mp4"

VEHICLE_CLASSES = {"car", "bus", "truck", "motorcycle"}
GRID_SIZE = (8, 8)              # finer = more precision
SMOOTH_WINDOW = 8               # temporal smoothing frames
CONF_THRESH = 0.3               # YOLO confidence
MIN_BOX_SIZE = 25               # ignore tiny detections
FRAME_RESIZE = 720              # height resize for speed

# ---------------- LOAD YOLO ----------------
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError("Error opening video")

# Read one frame to get dimensions
ret, frame = cap.read()
if not ret:
    raise RuntimeError("Empty video")

H0, W0 = frame.shape[:2]
scale = FRAME_RESIZE / H0
W, H = int(W0 * scale), FRAME_RESIZE
grid_h, grid_w = GRID_SIZE
cell_h, cell_w = H // grid_h, W // grid_w

history = deque(maxlen=SMOOTH_WINDOW)

# ---------------- MAIN LOOP ----------------
while ret:
    frame = cv2.resize(frame, (W, H))
    results = model(frame, conf=CONF_THRESH, verbose=False)[0]

    vehicle_mask = np.zeros((grid_h, grid_w), dtype=np.float32)
    vehicle_count = 0

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]
        if label not in VEHICLE_CLASSES:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w, h = x2 - x1, y2 - y1
        if w < MIN_BOX_SIZE or h < MIN_BOX_SIZE:
            continue
        vehicle_count += 1

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 180, 0), 2)

        # Mark occupied grid cells (approximate)
        r1, r2 = y1 // cell_h, y2 // cell_h
        c1, c2 = x1 // cell_w, x2 // cell_w
        vehicle_mask[r1:r2+1, c1:c2+1] = 1

    # Compute congestion metric
    coverage = vehicle_mask.mean() * 100  # % of grid covered
    metric = 0.6 * coverage + 0.4 * min(vehicle_count * 3, 100)  # combined score
    history.append(metric)
    smooth_metric = np.mean(history)

    # Congestion classification
    if smooth_metric < 25:
        status, color = "Light Traffic", (0, 255, 0)
    elif smooth_metric < 55:
        status, color = "Moderate Traffic", (0, 255, 255)
    else:
        status, color = "Heavy Traffic", (0, 0, 255)

    # Display
    cv2.putText(frame, f"Vehicles: {vehicle_count}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Congestion: {status} ({smooth_metric:.1f}%)", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Smart Traffic Congestion", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
