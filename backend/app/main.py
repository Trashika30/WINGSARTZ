import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.app.core.config import settings
from backend.app.api import auth, orders, inventory, shipping, admin, painter, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Arts & Crafts Platform Backend - WingsArtz",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/app") or request.url.path.endswith(".html") or request.url.path.endswith(".js"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# CORS - allow all configured origins including null (for local file:// access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure local uploads directory exists
UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for uploads
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Serve root project files (logo.jpeg etc.) under /assets
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@app.get("/logo.jpeg")
def serve_logo():
    logo_path = os.path.join(ROOT_DIR, "logo.jpeg")
    if os.path.isfile(logo_path):
        return FileResponse(logo_path, media_type="image/jpeg")
    return JSONResponse({"error": "logo not found"}, status_code=404)

# Serve frontend files directly from FastAPI at /app
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# Mount API endpoints
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(shipping.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(painter.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "WingsArtz API is running [OK]",
        "version": "1.0.0",
        "documentation": "/docs",
        "customer_portal": "/app/index.html",
        "admin_portal": "/app/admin.html",
        "api_base": "/api/v1"
    }
