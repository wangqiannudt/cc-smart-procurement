from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, get_processor_or_admin
from app.models.user import User, UserRole
from app.models.requirement import Requirement, RequirementStatus
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class RequirementCreate(BaseModel):
    title: str
    content: Optional[str] = None
    category: Optional[str] = None

class RequirementStatusUpdate(BaseModel):
    status: str
    processor_id: Optional[int] = None

@router.get("/")
async def get_requirements(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取需求列表（按角色过滤）"""
    query = db.query(Requirement)

    if current_user.role == UserRole.HANDLER.value:
        # 承办人只看自己的需求
        query = query.filter(Requirement.submitter_id == current_user.id)
    elif current_user.role == UserRole.PROCESSOR.value:
        # 经办人看待处理和处理中的需求
        query = query.filter(Requirement.status.in_([
            RequirementStatus.PENDING.value,
            RequirementStatus.PROCESSING.value
        ]))
    # 管理员看全部

    if status:
        query = query.filter(Requirement.status == status)

    requirements = query.order_by(Requirement.created_at.desc()).all()
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": [{
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "category": r.category,
                "status": r.status,
                "submitter_id": r.submitter_id,
                "submitter_name": r.submitter.username if r.submitter else None,
                "processor_id": r.processor_id,
                "processor_name": r.processor.username if r.processor else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None
            } for r in requirements]
        }
    )

@router.post("/")
async def create_requirement(
    req_data: RequirementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交新需求（承办人）"""
    requirement = Requirement(
        title=req_data.title,
        content=req_data.content,
        category=req_data.category,
        submitter_id=current_user.id,
        status=RequirementStatus.PENDING.value
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "id": requirement.id,
                "message": "需求提交成功"
            }
        }
    )

@router.get("/{req_id}")
async def get_requirement(
    req_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取需求详情"""
    requirement = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not requirement:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "需求不存在"}
        )
    # 数据权限检查
    if current_user.role == UserRole.HANDLER.value and requirement.submitter_id != current_user.id:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "无权访问此需求"}
        )
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "id": requirement.id,
                "title": requirement.title,
                "content": requirement.content,
                "category": requirement.category,
                "status": requirement.status,
                "submitter_id": requirement.submitter_id,
                "submitter_name": requirement.submitter.username if requirement.submitter else None,
                "processor_id": requirement.processor_id,
                "processor_name": requirement.processor.username if requirement.processor else None,
                "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
                "updated_at": requirement.updated_at.isoformat() if requirement.updated_at else None,
                "completed_at": requirement.completed_at.isoformat() if requirement.completed_at else None
            }
        }
    )

@router.put("/{req_id}/status")
async def update_requirement_status(
    req_id: int,
    status_data: RequirementStatusUpdate,
    current_user: User = Depends(get_processor_or_admin),
    db: Session = Depends(get_db)
):
    """更新需求状态（经办人/管理员）"""
    requirement = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not requirement:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "需求不存在"}
        )

    if status_data.status not in [s.value for s in RequirementStatus]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "无效的状态"}
        )

    requirement.status = status_data.status
    requirement.updated_at = datetime.utcnow()

    # 如果变为处理中且没有经办人，自动分配
    if status_data.status == RequirementStatus.PROCESSING.value and not requirement.processor_id:
        requirement.processor_id = current_user.id

    # 如果变为已完成，记录完成时间
    if status_data.status == RequirementStatus.COMPLETED.value:
        requirement.completed_at = datetime.utcnow()

    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "状态已更新"}}
    )

@router.put("/{req_id}/assign")
async def assign_requirement(
    req_id: int,
    processor_id: int,
    current_user: User = Depends(get_processor_or_admin),
    db: Session = Depends(get_db)
):
    """分配经办人（经办人/管理员）"""
    requirement = db.query(Requirement).filter(Requirement.id == req_id).first()
    if not requirement:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "需求不存在"}
        )

    processor = db.query(User).filter(User.id == processor_id).first()
    if not processor or processor.role not in [UserRole.PROCESSOR.value, UserRole.ADMIN.value]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "无效的经办人"}
        )

    requirement.processor_id = processor_id
    requirement.updated_at = datetime.utcnow()
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "已分配经办人"}}
    )
