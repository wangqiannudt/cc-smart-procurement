from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/")
async def get_users(
    role: str = None,
    is_active: bool = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（管理员）"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    users = query.all()
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": [{
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            } for u in users]
        }
    )

@router.put("/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """激活用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "用户不存在"}
        )
    user.is_active = True
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "用户已激活"}}
    )

@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """停用用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "用户不存在"}
        )
    user.is_active = False
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "用户已停用"}}
    )

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """修改用户角色（管理员）"""
    if role not in [r.value for r in UserRole]:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "无效的角色"}
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "用户不存在"}
        )
    user.role = role
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "角色已更新"}}
    )
