from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import or_
from datetime import datetime

from database import get_db, engine
from models import Base, User, Asset
from auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

# 创建用户请求模型
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

# 创建修改密码请求模型
class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# 创建资产请求模型
class AssetCreate(BaseModel):
    name: str
    type: str
    status: str = 'normal'
    location: Optional[str] = None
    purchase_date: Optional[datetime] = None
    description: Optional[str] = None

# 创建资产更新模型
class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[datetime] = None
    description: Optional[str] = None

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 登录接口
@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 注册接口
@app.post("/api/users", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证角色
    if user.role not in ["admin", "staff", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="无效的用户角色")
    
    # 验证手机号格式（如果提供）
    if user.phone and not user.phone.isdigit():
        raise HTTPException(status_code=400, detail="无效的手机号格式")
    
    # 验证邮箱格式（如果提供）
    if user.email and "@" not in user.email:
        raise HTTPException(status_code=400, detail="无效的邮箱格式")
    
    # 创建新用户
    try:
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            password=hashed_password,
            role=user.role,
            real_name=user.real_name,
            phone=user.phone,
            email=user.email
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "注册成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"注册失败：{str(e)}")

# 获取当前用户信息接口
@app.get("/api/users/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "real_name": current_user.real_name,
        "phone": current_user.phone,
        "email": current_user.email
    }

# 更新当前用户信息接口
@app.put("/api/users/me", response_model=dict)
async def update_current_user_info(user_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # 验证手机号格式（如果提供）
        if user_data.get('phone') and not user_data['phone'].isdigit():
            raise HTTPException(status_code=400, detail="无效的手机号格式")
        
        # 验证邮箱格式（如果提供）
        if user_data.get('email') and "@" not in user_data['email']:
            raise HTTPException(status_code=400, detail="无效的邮箱格式")
        
        # 更新用户信息
        for key, value in user_data.items():
            if key not in ['password', 'username', 'role'] and hasattr(current_user, key):
                setattr(current_user, key, value)
        
        db.commit()
        return {"message": "更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{str(e)}")

# 修改密码接口
@app.put("/api/users/me/password", response_model=dict)
async def change_password(password_data: ChangePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 验证旧密码
    if not authenticate_user(db, current_user.username, password_data.old_password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    # 更新密码
    try:
        current_user.password = get_password_hash(password_data.new_password)
        db.commit()
        return {"message": "密码修改成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"密码修改失败：{str(e)}")

# 获取资产列表
@app.get("/api/assets")
async def get_assets(
    page: int = 1,
    page_size: int = 10,
    type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Asset)
        # 应用筛选条件
        if type:
            query = query.filter(Asset.type == type)
        if status:
            query = query.filter(Asset.status == status)
        if search:
            query = query.filter(
                or_(
                    Asset.name.ilike(f"%{search}%"),
                    Asset.location.ilike(f"%{search}%"),
                    Asset.description.ilike(f"%{search}%")
                )
            )
        # 计算总数
        total = query.count()
        # 分页
        assets = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": asset.id,
            "name": asset.name,
            "type": asset.type,
            "status": asset.status,
            "location": asset.location,
            "purchase_date": asset.purchase_date,
            "description": asset.description
        } for asset in assets]
        
        return {"items": result, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资产列表失败：{str(e)}")

# 添加资产
@app.post("/api/assets", response_model=dict)
async def createAsset(asset: AssetCreate, db: Session = Depends(get_db)):
    try:
        # 验证资产类型
        if asset.type not in ['教学设备', '办公设备', '实验设备', '体育器材', '其他']:
            raise HTTPException(status_code=400, detail="无效的资产类型")
        
        # 验证资产状态
        if asset.status not in ['normal', 'repair', 'scrapped']:
            raise HTTPException(status_code=400, detail="无效的资产状态")
        
        # 创建新资产
        new_asset = Asset(**asset.dict())
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        return {"message": "添加成功", "id": new_asset.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败：{str(e)}")

# 更新资产
@app.put("/api/assets/{asset_id}", response_model=dict)
async def updateAsset(asset_id: int, asset: AssetUpdate, db: Session = Depends(get_db)):
    try:
        # 查找资产
        db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not db_asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 验证资产类型
        if asset.type and asset.type not in ['教学设备', '办公设备', '实验设备', '体育器材', '其他']:
            raise HTTPException(status_code=400, detail="无效的资产类型")
        
        # 验证资产状态
        if asset.status and asset.status not in ['normal', 'repair', 'scrapped']:
            raise HTTPException(status_code=400, detail="无效的资产状态")
        
        # 更新资产信息
        for key, value in asset.dict(exclude_unset=True).items():
            setattr(db_asset, key, value)
        
        db.commit()
        return {"message": "更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{str(e)}")

# 删除资产
@app.delete("/api/assets/{asset_id}", response_model=dict)
async def deleteAsset(asset_id: int, db: Session = Depends(get_db)):
    try:
        # 查找资产
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="资产不存在")
        
        # 删除资产
        db.delete(asset)
        db.commit()
        return {"message": "删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除失败：{str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)