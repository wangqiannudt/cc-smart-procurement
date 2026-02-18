# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Smart Procurement System API",
    description="智慧采购系统后端API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "Smart Procurement System is running",
            "version": "1.0.0"
        }
    )

# Database initialization
from app.core.database import init_db, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.analysis_history import AnalysisHistory

@app.on_event("startup")
async def startup_event():
    init_db()

    # 创建初始管理员账号
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN.value,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("初始管理员账号已创建: admin / admin123")
    finally:
        db.close()

# Import routes
from app.api import (
    requirements,
    price,
    contract,
    chat,
    auth,
    users,
    requirements_mgmt,
    statistics,
    analysis,
)

# Register routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(requirements.router, prefix="/api", tags=["requirements"])
app.include_router(requirements_mgmt.router, prefix="/api/requirements", tags=["requirements_mgmt"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(price.router, prefix="/api", tags=["price"])
app.include_router(contract.router, prefix="/api", tags=["contract"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
