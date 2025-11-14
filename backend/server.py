# # server.py
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse

# app = FastAPI()

# # Shared memory storage (you can later switch to Redis or DB)
# latest_metrics = {"counts": {}, "overall_congestion": 0.0}

# @app.post("/metrics")
# async def receive_metrics(request: Request):
#     """Receive data from Vision model."""
#     global latest_metrics
#     data = await request.json()
#     latest_metrics = data
#     return {"status": "ok"}

# @app.get("/metrics")
# def get_metrics():
#     """Let the signal optimizer fetch latest metrics."""
#     return JSONResponse(latest_metrics)

# @app.post("/signal-update")
# async def update_signal(request: Request):
#     """Optional — receive optimizer's actions for logging."""
#     data = await request.json()
#     print(f"[SIGNAL UPDATE] {data}")
#     return {"status": "signal updated"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)
# server.py
# backend/server.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Metrics(BaseModel):
    counts: dict
    overall_congestion: float

@app.post("/metrics")
def optimize_signal(data: Metrics):
    counts = data.counts
    congestion = data.overall_congestion

    base_time = 20  # base green time for each direction
    total = sum(counts.values()) + 1e-6
    optimized = {}

    # Realistic optimization logic
    for direction, count in counts.items():
        ratio = count / total
        if congestion > 60:
            time = base_time + ratio * 40
        elif congestion > 30:
            time = base_time + ratio * 25
        else:
            time = base_time + ratio * 10
        optimized[direction] = round(max(10, min(time, 60)), 1)

    return {
        "original_timings": {d: base_time for d in counts},
        "optimized_timings": optimized,
        "overall_congestion": congestion
    }
