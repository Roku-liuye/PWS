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
from models import Base, User, Asset, Repair, Notice
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
        if asset.type not in ['教学设备', '办公设备', '实验设备', '设施设备', '体育器材', '其他']:
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
        if asset.type and asset.type not in ['教学设备', '办公设备', '实验设备', '设施设备', '体育器材', '其他']:
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

# 创建报修请求模型
class RepairCreate(BaseModel):
    type: str
    location: str
    description: str

# 创建报修更新模型
class RepairUpdate(BaseModel):
    status: Optional[str] = None
    complete_time: Optional[datetime] = None

# 获取报修列表
@app.get("/api/repairs")
async def get_repairs(
    page: int = 1,
    page_size: int = 10,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Repair)
        # 应用筛选条件
        if type:
            query = query.filter(Repair.type == type)
        if status:
            query = query.filter(Repair.status == status)
        
        # 计算总数
        total = query.count()
        # 分页
        repairs = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": repair.id,
            "type": repair.type,
            "location": repair.location,
            "description": repair.description,
            "status": repair.status,
            "submit_time": repair.submit_time,
            "complete_time": repair.complete_time
        } for repair in repairs]
        
        return {
            "total": total,
            "items": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取报修列表失败：{str(e)}")

# 创建报修
@app.post("/api/repairs")
async def create_repair(
    repair: RepairCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        
        # 创建报修记录
        new_repair = Repair(
            type=repair.type,
            location=repair.location,
            description=repair.description,
            status="pending",
            submitter_id=current_user.id
        )
        
        db.add(new_repair)
        db.commit()
        db.refresh(new_repair)
        
        return {
            "id": new_repair.id,
            "type": new_repair.type,
            "location": new_repair.location,
            "description": new_repair.description,
            "status": new_repair.status,
            "submit_time": new_repair.submit_time
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建报修失败：{str(e)}")

# 更新报修状态
@app.put("/api/repairs/{repair_id}")
async def update_repair(
    repair_id: int,
    repair_update: RepairUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 查找报修记录
        repair = db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(status_code=404, detail="报修记录不存在")
        
        # 更新状态
        if repair_update.status:
            repair.status = repair_update.status
        if repair_update.complete_time:
            repair.complete_time = repair_update.complete_time
        
        db.commit()
        db.refresh(repair)
        
        return {
            "id": repair.id,
            "type": repair.type,
            "location": repair.location,
            "description": repair.description,
            "status": repair.status,
            "submit_time": repair.submit_time,
            "complete_time": repair.complete_time
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新报修状态失败：{str(e)}")

# 获取维修人员列表
@app.get("/api/users/staff")
async def get_staff_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        staff = db.query(User).filter(User.role == "staff").all()
        return {
            "items": [
                {
                    "id": user.id,
                    "real_name": user.real_name,
                    "phone": user.phone,
                    "email": user.email
                } for user in staff
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取维修人员列表失败：{str(e)}")

# 获取维修列表
@app.get("/api/maintenance")
async def get_maintenance_list(
    page_num: int = 1,
    page_size: int = 10,
    repair_no: Optional[str] = None,
    status: Optional[str] = None,
    maintainer: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Repair)
        
        # 应用筛选条件
        if repair_no:
            query = query.filter(Repair.repair_id == repair_no)
        if status:
            query = query.filter(Repair.status == status)
        if maintainer:
            query = query.filter(Repair.maintainer_id == maintainer)
            
        # 计算总数
        total = query.count()
        # 分页
        repairs = query.offset((page_num - 1) * page_size).limit(page_size).all()
        
        return {
            "items": [
                {
                    "id": repair.id,
                    "repair_id": repair.repair_id,
                    "type": repair.type,
                    "location": repair.location,
                    "description": repair.description,
                    "status": repair.status,
                    "maintainer_id": repair.maintainer_id,
                    "assign_time": repair.assign_time,
                    "expected_time": repair.expected_time
                } for repair in repairs
            ],
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取维修列表失败：{str(e)}")

# 获取用户列表
@app.get("/api/users")
async def get_users(
    page: int = 1,
    page_size: int = 10,
    username: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(User)
        
        # 应用筛选条件
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))
        if role:
            query = query.filter(User.role == role)
        
        # 计算总数
        total = query.count()
        
        # 分页
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "real_name": user.real_name,
            "phone": user.phone,
            "email": user.email,
            "status": "active"  # 暂时默认所有用户都是激活状态
        } for user in users]
        
        return {"items": result, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败：{str(e)}")

# 创建公告请求模型
class NoticeCreate(BaseModel):
    title: str
    content: str
    status: str = 'published'

# 创建公告更新模型
class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None

# 获取公告列表
@app.get("/api/notices")
async def get_notices(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Notice)
        
        # 计算总数
        total = query.count()
        # 分页
        notices = query.order_by(Notice.publish_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": notice.id,
            "title": notice.title,
            "content": notice.content,
            "publisher_id": notice.publisher_id,
            "publish_time": notice.publish_time,
            "status": notice.status
        } for notice in notices]
        
        return {"items": result, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告列表失败：{str(e)}")

# 创建公告
@app.post("/api/notices")
async def create_notice(
    notice: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 验证状态
        if notice.status not in ['draft', 'published', 'archived']:
            raise HTTPException(status_code=400, detail="无效的公告状态")
        
        # 创建新公告
        new_notice = Notice(
            title=notice.title,
            content=notice.content,
            status=notice.status,
            publisher_id=current_user.id
        )
        
        db.add(new_notice)
        db.commit()
        db.refresh(new_notice)
        
        return {
            "id": new_notice.id,
            "title": new_notice.title,
            "content": new_notice.content,
            "publisher_id": new_notice.publisher_id,
            "publish_time": new_notice.publish_time,
            "status": new_notice.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建公告失败：{str(e)}")

# 更新公告
@app.put("/api/notices/{notice_id}")
async def update_notice(
    notice_id: int,
    notice: NoticeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 查找公告
        db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
        if not db_notice:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 验证状态
        if notice.status and notice.status not in ['draft', 'published', 'archived']:
            raise HTTPException(status_code=400, detail="无效的公告状态")
        
        # 更新公告信息
        for key, value in notice.dict(exclude_unset=True).items():
            setattr(db_notice, key, value)
        
        db.commit()
        db.refresh(db_notice)
        
        return {
            "id": db_notice.id,
            "title": db_notice.title,
            "content": db_notice.content,
            "publisher_id": db_notice.publisher_id,
            "publish_time": db_notice.publish_time,
            "status": db_notice.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新公告失败：{str(e)}")

# 删除公告
@app.delete("/api/notices/{notice_id}")
async def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 查找公告
        notice = db.query(Notice).filter(Notice.id == notice_id).first()
        if not notice:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 删除公告
        db.delete(notice)
        db.commit()
        return {"message": "删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除公告失败：{str(e)}")

# 教室相关的请求模型
class ClassroomCreate(BaseModel):
    room_no: str
    building: str
    floor: int
    capacity: int
    description: Optional[str] = None

class ClassroomUpdate(BaseModel):
    room_no: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None

class ClassroomBookingCreate(BaseModel):
    classroom_id: int
    purpose: str
    start_time: datetime
    end_time: datetime

# 获取教室列表
@app.get("/api/classrooms")
async def get_classrooms(
    page: int = 1,
    page_size: int = 10,
    building: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Classroom)
        
        # 应用筛选条件
        if building:
            query = query.filter(Classroom.building == building)
        if status:
            query = query.filter(Classroom.status == status)
        
        # 计算总数
        total = query.count()
        # 分页
        classrooms = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": classroom.id,
            "room_no": classroom.room_no,
            "building": classroom.building,
            "floor": classroom.floor,
            "capacity": classroom.capacity,
            "status": classroom.status,
            "description": classroom.description
        } for classroom in classrooms]
        
        return {"total": total, "list": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取教室列表失败：{str(e)}")

# 添加教室
@app.post("/api/classrooms", response_model=dict)
async def create_classroom(
    classroom: ClassroomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 检查教室编号是否已存在
        existing_classroom = db.query(Classroom).filter(Classroom.room_no == classroom.room_no).first()
        if existing_classroom:
            raise HTTPException(status_code=400, detail="教室编号已存在")
        
        # 创建新教室
        new_classroom = Classroom(**classroom.dict())
        db.add(new_classroom)
        db.commit()
        db.refresh(new_classroom)
        return {"message": "添加成功", "id": new_classroom.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败：{str(e)}")

# 更新教室信息
@app.put("/api/classrooms/{classroom_id}", response_model=dict)
async def update_classroom(
    classroom_id: int,
    classroom: ClassroomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 查找教室
        db_classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if not db_classroom:
            raise HTTPException(status_code=404, detail="教室不存在")
        
        # 更新教室信息
        for key, value in classroom.dict(exclude_unset=True).items():
            setattr(db_classroom, key, value)
        
        db.commit()
        return {"message": "更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{str(e)}")

# 删除教室
@app.delete("/api/classrooms/{classroom_id}", response_model=dict)
async def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 查找教室
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if not classroom:
            raise HTTPException(status_code=404, detail="教室不存在")
        
        # 删除教室
        db.delete(classroom)
        db.commit()
        return {"message": "删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除失败：{str(e)}")

# 获取教室预约列表
@app.get("/api/classroom-bookings")
async def get_classroom_bookings(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(ClassroomBooking)
        
        # 应用筛选条件
        if status:
            query = query.filter(ClassroomBooking.status == status)
        if date:
            query = query.filter(func.date(ClassroomBooking.start_time) == date)
        
        # 计算总数
        total = query.count()
        # 分页
        bookings = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        result = [{
            "id": booking.id,
            "classroom_id": booking.classroom_id,
            "user_id": booking.user_id,
            "purpose": booking.purpose,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "status": booking.status
        } for booking in bookings]
        
        return {"total": total, "list": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预约列表失败：{str(e)}")

# 创建教室预约
@app.post("/api/classroom-bookings", response_model=dict)
async def create_classroom_booking(
    booking: ClassroomBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 检查教室是否存在
        classroom = db.query(Classroom).filter(Classroom.id == booking.classroom_id).first()
        if not classroom:
            raise HTTPException(status_code=404, detail="教室不存在")
        
        # 检查时间段是否冲突
        existing_booking = db.query(ClassroomBooking).filter(
            ClassroomBooking.classroom_id == booking.classroom_id,
            ClassroomBooking.status == "approved",
            ClassroomBooking.start_time < booking.end_time,
            ClassroomBooking.end_time > booking.start_time
        ).first()
        
        if existing_booking:
            raise HTTPException(status_code=400, detail="该时间段已被预约")
        
        # 创建预约
        new_booking = ClassroomBooking(
            classroom_id=booking.classroom_id,
            user_id=current_user.id,
            purpose=booking.purpose,
            start_time=booking.start_time,
            end_time=booking.end_time
        )
        
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return {"message": "预约申请提交成功", "id": new_booking.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"预约失败：{str(e)}")

# 更新预约状态
@app.put("/api/classroom-bookings/{booking_id}", response_model=dict)
async def update_classroom_booking(
    booking_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 检查预约是否存在
        booking = db.query(ClassroomBooking).filter(ClassroomBooking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="预约记录不存在")
        
        # 更新状态
        booking.status = status
        db.commit()
        return {"message": "更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{str(e)}")

# 费用管理相关模型
class FinanceCreate(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = None
    record_time: datetime

class FinanceUpdate(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    record_time: Optional[datetime] = None

# 获取费用列表
@app.get("/api/finances")
async def get_finances(
    page_num: int = 1,
    page_size: int = 10,
    type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Finance)
    
    if type:
        query = query.filter(Finance.type == type)
    if start_date:
        query = query.filter(Finance.record_time >= start_date)
    if end_date:
        query = query.filter(Finance.record_time <= end_date)
    
    total = query.count()
    finances = query.offset((page_num - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": finance.id,
                "type": finance.type,
                "amount": finance.amount,
                "category": finance.category,
                "description": finance.description,
                "record_time": finance.record_time,
                "created_at": finance.created_at,
                "updated_at": finance.updated_at
            } for finance in finances
        ]
    }

# 创建费用记录
@app.post("/api/finances")
async def create_finance(
    finance: FinanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_finance = Finance(**finance.dict())
        db.add(new_finance)
        db.commit()
        db.refresh(new_finance)
        return new_finance
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建费用记录失败：{str(e)}")

# 更新费用记录
@app.put("/api/finances/{finance_id}")
async def update_finance(
    finance_id: int,
    finance: FinanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_finance = db.query(Finance).filter(Finance.id == finance_id).first()
        if not db_finance:
            raise HTTPException(status_code=404, detail="费用记录不存在")
        
        for key, value in finance.dict(exclude_unset=True).items():
            setattr(db_finance, key, value)
        
        db.commit()
        db.refresh(db_finance)
        return db_finance
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新费用记录失败：{str(e)}")

# 删除费用记录
@app.delete("/api/finances/{finance_id}")
async def delete_finance(
    finance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        finance = db.query(Finance).filter(Finance.id == finance_id).first()
        if not finance:
            raise HTTPException(status_code=404, detail="费用记录不存在")
        
        db.delete(finance)
        db.commit()
        return {"message": "删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除费用记录失败：{str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)