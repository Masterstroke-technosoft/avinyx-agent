from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Global exception handler to prevent leaking sensitive tracebacks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

import threading
from app.workers.text_agent import start_worker as start_text_agent
from app.workers.critical_agent import start_worker as start_critical_agent
from app.workers.geo_agent import start_worker as start_geo_agent
from app.workers.vision_agent import start_worker as start_vision_agent

@app.on_event("startup")
def startup_event():
    print("🚀 Starting AI Agent Workers in the background...")
    
    agents = [
        ("Text Agent", start_text_agent),
        ("Critical Agent", start_critical_agent),
        ("Geo Agent", start_geo_agent),
        ("Vision Agent", start_vision_agent)
    ]
    
    for name, agent_func in agents:
        thread = threading.Thread(target=agent_func, daemon=True, name=name)
        thread.start()
        print(f"✅ {name} thread started.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic System API"}
