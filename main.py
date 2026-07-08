from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

# 1. Custom Middleware to inject X-Request-ID and X-Process-Time
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    # Format as a non-negative decimal (e.g., 0.001234)
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# 2. Strict CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dash-irxkv0.example.com"], # ONLY this origin is allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. The /stats Endpoint
@app.get("/stats")
async def get_stats(values: str = Query(...)):
    try:
        # Parse comma-separated integers
        vals = [int(v) for v in values.split(",")]
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid values format"})
    
    if not vals:
        return JSONResponse(status_code=400, content={"error": "No values provided"})

    # Compute descriptive statistics
    count = len(vals)
    total = sum(vals)
    min_val = min(vals)
    max_val = max(vals)
    mean_val = total / count

    # REPLACE THIS WITH YOUR ACTUAL LOGGED-IN EMAIL
    email = "25f1000659@ds.study.iitm.ac.in" 

    return {
        "email": email,
        "count": count,
        "sum": total,
        "min": min_val,
        "max": max_val,
        "mean": mean_val
    }