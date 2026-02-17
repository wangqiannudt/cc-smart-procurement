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

# Import routes
from app.api import requirements, price, contract, chat

# Register routes
app.include_router(requirements.router, prefix="/api", tags=["requirements"])
app.include_router(price.router, prefix="/api", tags=["price"])
app.include_router(contract.router, prefix="/api", tags=["contract"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
