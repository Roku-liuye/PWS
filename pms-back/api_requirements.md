# 物业管理系统后端API需求文档

后端启动命令 uvicorn main:app --reload

## 1. 系统概述

本系统是一个基于FastAPI的物业管理系统后端，提供用户管理、资产管理、报修管理、维修分配、费用管理、教室租借和公告管理等功能的API接口。

## 2. 技术栈

- FastAPI：Web框架
- SQLAlchemy：ORM框架
- MySQL：数据库
- JWT：身份认证

## 3. 数据模型

### 3.1 用户模型（User）
```python
class User:
    id: int
    username: str
    password: str
    role: str  # admin, staff, user
    name: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime
```

### 3.2 资产模型（Asset）
```python
class Asset:
    id: int
    name: str
    type: str  # equipment, facility
    location: str
    status: str  # in_use, maintenance, scrapped
    purchase_date: date
    price: float
    description: str
    created_at: datetime
    updated_at: datetime
```

### 3.3 报修工单（Repair）
```python
class Repair:
    id: int
    repair_no: str
    user_id: int
    asset_id: int
    type: str  # equipment, facility
    location: str
    description: str
    status: str  # pending, processing, completed
    maintainer_id: int
    submit_time: datetime
    complete_time: datetime
    created_at: datetime
    updated_at: datetime
```

### 3.4 费用记录（Finance）
```python
class Finance:
    id: int
    type: str  # income, expense
    amount: float
    category: str
    description: str
    record_time: datetime
    created_at: datetime
    updated_at: datetime
```

### 3.5 教室租借（Classroom）
```python
class ClassroomBooking:
    id: int
    classroom_id: int
    user_id: int
    purpose: str
    start_time: datetime
    end_time: datetime
    status: str  # pending, approved, rejected
    created_at: datetime
    updated_at: datetime
```

### 3.6 系统公告（Notice）
```python
class Notice:
    id: int
    title: str
    content: str
    publisher_id: int
    publish_time: datetime
    created_at: datetime
    updated_at: datetime
```

## 4. API接口设计

### 4.1 用户管理

#### 登录
- POST /api/auth/login
- 请求体：{"username": string, "password": string}
- 响应：{"access_token": string, "token_type": string}

#### 获取用户信息
- GET /api/users/me
- 请求头：Authorization: Bearer {token}
- 响应：User对象

#### 用户列表
- GET /api/users
- 查询参数：page_num, page_size, role
- 响应：{"total": number, "items": User[]}

### 4.2 资产管理

#### 资产列表
- GET /api/assets
- 查询参数：page_num, page_size, type, status
- 响应：{"total": number, "items": Asset[]}

#### 添加资产
- POST /api/assets
- 请求体：Asset对象（不含id）
- 响应：Asset对象

### 4.3 报修管理

#### 报修列表
- GET /api/repairs
- 查询参数：page_num, page_size, status, type
- 响应：{"total": number, "items": Repair[]}

#### 提交报修
- POST /api/repairs
- 请求体：Repair对象（不含id）
- 响应：Repair对象

#### 分配维修人员
- PUT /api/repairs/{repair_id}/assign
- 请求体：{"maintainer_id": number}
- 响应：Repair对象

### 4.4 费用管理

#### 费用列表
- GET /api/finances
- 查询参数：page_num, page_size, type, start_date, end_date
- 响应：{"total": number, "items": Finance[]}

#### 添加费用记录
- POST /api/finances
- 请求体：Finance对象（不含id）
- 响应：Finance对象

### 4.5 教室租借

#### 教室预约列表
- GET /api/classroom-bookings
- 查询参数：page_num, page_size, status, date
- 响应：{"total": number, "items": ClassroomBooking[]}

#### 提交预约
- POST /api/classroom-bookings
- 请求体：ClassroomBooking对象（不含id）
- 响应：ClassroomBooking对象

### 4.6 公告管理

#### 公告列表
- GET /api/notices
- 查询参数：page_num, page_size
- 响应：{"total": number, "items": Notice[]}

#### 发布公告
- POST /api/notices
- 请求体：Notice对象（不含id）
- 响应：Notice对象

## 5. 权限控制

- 管理员（admin）：所有操作权限
- 工作人员（staff）：资产管理、维修分配、费用管理权限
- 普通用户（user）：查看信息、提交报修、预约教室权限

## 6. 错误处理

统一的错误响应格式：
```json
{
    "code": number,
    "message": string,
    "detail": string
}
```

常见错误码：
- 400：请求参数错误
- 401：未授权
- 403：权限不足
- 404：资源不存在
- 500：服务器内部错误

## 7. 数据验证

使用Pydantic模型进行：
- 请求参数验证
- 响应数据格式化
- 数据类型转换

## 8. 安全性考虑

- 使用JWT进行身份认证
- 密码加密存储
- SQL注入防护
- CORS配置
- 请求频率限制