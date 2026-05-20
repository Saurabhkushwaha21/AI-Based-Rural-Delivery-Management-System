from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from database import Base, engine
import models   # IMPORTANT: models load before create_all()

# ===== ROUTERS =====
from auth1 import router as auth_router
from routes.auth import router as otp_router
from routes.orders import router as order_router
from routes.hubs import router as hub_router
from routes.delivery import router as delivery_router
from routes.ml import router as ml_router
from routes.tracking import router as tracking_router

# ================= APP =================
app = FastAPI(
    title="RuralDeliver API",
    version="1.0.0"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "https://ai-based-rural-delivery-management.netlify.app",
        "https://ai-based-rural-delivery-management-system.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DB INIT =================
Base.metadata.create_all(bind=engine)

# ================= ROUTERS =================
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(otp_router, prefix="/api/auth", tags=["OTP Auth"])
app.include_router(order_router, prefix="/api/orders", tags=["Orders"])
app.include_router(hub_router, prefix="/api/hubs", tags=["Hubs"])
app.include_router(delivery_router, prefix="/api/delivery", tags=["Delivery"])
app.include_router(ml_router, prefix="/api/ml", tags=["ML"])
app.include_router(tracking_router, prefix="/api/tracking", tags=["Tracking"])

# ================= ROOT =================
@app.get("/")
def root():
    return {"message": "API Working 🚀"}

@app.get("/test")
def test():
    return {"status": "Server OK ✅"}

# ================= ERROR HANDLERS =================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": exc.errors()}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 ERROR:", str(exc))
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"message": "Something went wrong!"}
    )