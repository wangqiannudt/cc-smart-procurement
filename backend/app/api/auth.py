from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse, ChangePassword

router = APIRouter()

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "用户名已存在"}
        )
    # 检查邮箱是否存在
    if db.query(User).filter(User.email == user_data.email).first():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "邮箱已存在"}
        )
    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {"message": "注册成功，请等待管理员审核激活"}
        }
    )

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "用户名或密码错误"}
        )
    if not user.is_active:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "账号未激活，请等待管理员审核"}
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }
        }
    )

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role,
                "is_active": current_user.is_active,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            }
        }
    )

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "原密码错误"}
        )
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    return JSONResponse(
        status_code=200,
        content={"success": True, "data": {"message": "密码修改成功"}}
    )
