# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uvicorn, csv, time, os

app = FastAPI(title="Smart Signal Optimizer API")
LOG_CSV = "optimizer_log.csv"

class Metrics(BaseModel):
    counts: Dict[str,int]
    queues: Dict[str,int] = None
    overall_congestion: float = 0.0

def optimize_signal(counts, queues=None, overall_congestion=0.0):
    # adaptive base_time derived from counts
    total = sum(counts.values()) + 1e-6
    # base time increases with total vehicles, bounded
    base_time = max(8.0, min(25.0, 8.0 + (total/4.0)))
    weights = {}
    for d,v in counts.items():
        q = (queues.get(d,0) if queues else 0)
        weights[d] = max(0.1, v + 2*q)
    s = sum(weights.values())
    scale = 50.0 if overall_congestion>70 else 30.0 if overall_congestion>40 else 15.0
    raw = {d: max(8.0, min(60.0, round(base_time + (weights[d]/s)*scale,1))) for d in weights}
    # normalize to 120s total cycle optionally
    total_alloc = sum(raw.values())
    TOTAL_CYCLE = 120.0
    if total_alloc > TOTAL_CYCLE:
        factor = TOTAL_CYCLE / total_alloc
        raw = {k: round(v*factor,1) for k,v in raw.items()}
    return {"base": {d: round(base_time,1) for d in counts}, "optimized": raw}

@app.post("/metrics")
async def receive(m: Metrics):
    res = optimize_signal(m.counts, m.queues or {}, m.overall_congestion)
    # log
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV,'w',newline='') as f:
            w = csv.writer(f); w.writerow(["ts","counts","queues","cong","base","opt"])
    with open(LOG_CSV,'a',newline='') as f:
        w = csv.writer(f)
        w.writerow([time.time(), m.counts, m.queues, m.overall_congestion, res["base"], res["optimized"]])
    return {"original_timings": res["base"], "optimized_timings": res["optimized"]}

@app.get("/signals")
def get_signals():
    # return last row of CSV if exists
    if os.path.exists(LOG_CSV):
        with open(LOG_CSV,'r') as f:
            rows = list(csv.reader(f))
            if len(rows)>1:
                last = rows[-1]
                return {"last": last}
    return {"last": None}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
