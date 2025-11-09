import cv2
from ultralytics import YOLO
import numpy as np


vehicle_classes = ["car", "truck", "bus", "motorcycle"]
min_box_size = 20
grid_size = (10, 10)  

# ---------------- YOLOv8 Model ----------------
model = YOLO("yolov8m.pt") 

# ---------------- Video Capture ----------------
video_path = "video1.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video file")
    exit()

ret, frame = cap.read()
frame_height, frame_width = frame.shape[:2]


while ret:
    results = model(frame, conf=0.25)[0]

    vehicles_current = 0
    vehicle_cells = np.zeros(grid_size, dtype=np.int32)

    cell_h = frame_height // grid_size[0]
    cell_w = frame_width // grid_size[1]

    for r in results.boxes:
        cls = int(r.cls[0])
        label = model.names[cls]
        if label not in vehicle_classes:
            continue

        x1, y1, x2, y2 = map(int, r.xyxy[0])
        w, h = x2 - x1, y2 - y1
        if w < min_box_size or h < min_box_size:
            continue

        vehicles_current += 1


        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

  
        top_cell = y1 // cell_h
        bottom_cell = y2 // cell_h
        left_cell = x1 // cell_w
        right_cell = x2 // cell_w
        vehicle_cells[top_cell:bottom_cell+1, left_cell:right_cell+1] = 1

    # ---------------- Congestion Calculation ----------------
    occupancy_percent = (vehicle_cells.sum() / (grid_size[0] * grid_size[1])) * 100

    if occupancy_percent < 20:
        congestion = "Light Traffic"
        color = (0, 255, 0)
    elif occupancy_percent < 50:
        congestion = "Moderate Traffic"
        color = (0, 255, 255)
    else:
        congestion = "Heavy Traffic"
        color = (0, 0, 255)

    # ---------------- Display Info ----------------
    cv2.putText(frame, f"Vehicles in Frame: {vehicles_current}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 170, 0), 2)
    cv2.putText(frame, f"Congestion: {congestion} ({occupancy_percent:.1f}%)", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


    cv2.imshow("Accurate Congestion Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()




