from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-irxkv0.example.com"

# 1. Custom Middleware for Headers AND Strict CORS
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    origin = request.headers.get("origin")
    
    # --- PREFLIGHT (OPTIONS) HANDLING ---
    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            # Allowed origin: succeed and return ACAO header
            response = JSONResponse(content={"ok": True}, status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        else:
            # Evil origin: reject preflight (no ACAO header)
            response = JSONResponse(content={"error": "Disallowed origin"}, status_code=403)
            
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response

    # --- NORMAL REQUEST (GET) HANDLING ---
    response = await call_next(request)
    
    # Only add the CORS header if the request is from the allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# 2. The /stats Endpoint
@app.get("/stats")
async def get_stats(request: Request):
    # Get the raw 'values' query parameter directly to avoid FastAPI's default 422 errors
    values_param = request.query_params.get("values", "")
    
    if not values_param:
        return JSONResponse(status_code=400, content={"detail": "Missing values parameter"})
        
    try:
        # Strictly split by comma and convert to integers
        vals = [int(v.strip()) for v in values_param.split(",") if v.strip()]
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid values format"})

    if not vals:
        return JSONResponse(status_code=400, content={"detail": "No values provided"})

    # Compute descriptive statistics
    count = len(vals)
    total = sum(vals)
    min_val = min(vals)
    max_val = max(vals)
    mean_val = total / count

    return {
        "email": "25f1000659@ds.study.iitm.ac.in",
        "count": count,
        "sum": total,
        "min": min_val,
        "max": max_val,
        "mean": mean_val
    }