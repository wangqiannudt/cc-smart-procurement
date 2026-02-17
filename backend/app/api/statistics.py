from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.user import User, UserRole
from app.models.requirement import Requirement, RequirementStatus
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_overview(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """综合概览"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_requirements = db.query(Requirement).count()
    pending = db.query(Requirement).filter(Requirement.status == RequirementStatus.PENDING.value).count()
    processing = db.query(Requirement).filter(Requirement.status == RequirementStatus.PROCESSING.value).count()
    completed = db.query(Requirement).filter(Requirement.status == RequirementStatus.COMPLETED.value).count()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "total_users": total_users,
                "active_users": active_users,
                "total_requirements": total_requirements,
                "pending": pending,
                "processing": processing,
                "completed": completed
            }
        }
    )

@router.get("/processor-workload")
async def get_processor_workload(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """经办人工作量统计"""
    processors = db.query(User).filter(User.role == UserRole.PROCESSOR.value).all()
    result = []
    for p in processors:
        count = db.query(Requirement).filter(Requirement.processor_id == p.id).count()
        result.append({
            "id": p.id,
            "username": p.username,
            "total_processed": count
        })
    return JSONResponse(status_code=200, content={"success": True, "data": result})

@router.get("/submitter-requests")
async def get_submitter_requests(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """承办人需求量统计"""
    handlers = db.query(User).filter(User.role == UserRole.HANDLER.value).all()
    result = []
    for h in handlers:
        count = db.query(Requirement).filter(Requirement.submitter_id == h.id).count()
        result.append({
            "id": h.id,
            "username": h.username,
            "total_submitted": count
        })
    return JSONResponse(status_code=200, content={"success": True, "data": result})

@router.get("/processing-time")
async def get_processing_time(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """处理时效统计"""
    completed_reqs = db.query(Requirement).filter(
        Requirement.status == RequirementStatus.COMPLETED.value,
        Requirement.completed_at.isnot(None)
    ).all()

    if not completed_reqs:
        return JSONResponse(
            status_code=200,
            content={"success": True, "data": {"average_hours": 0, "total_completed": 0}}
        )

    total_hours = 0
    for r in completed_reqs:
        if r.created_at and r.completed_at:
            delta = r.completed_at - r.created_at
            total_hours += delta.total_seconds() / 3600

    avg_hours = total_hours / len(completed_reqs)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "average_hours": round(avg_hours, 2),
                "total_completed": len(completed_reqs)
            }
        }
    )

@router.get("/category-summary")
async def get_category_summary(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """采购分类统计"""
    result = db.query(
        Requirement.category,
        func.count(Requirement.id).label("count")
    ).group_by(Requirement.category).all()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": [{
                "category": r.category or "未分类",
                "count": r.count
            } for r in result]
        }
    )
