// API服务层，统一管理后端接口调用
import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:8000', // 后端API基础URL
  timeout: 5000 // 请求超时时间
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    if (error.response && error.response.data && error.response.data.detail) {
      return Promise.reject(new Error(error.response.data.detail))
    }
    return Promise.reject(error)
  }
)

// 用户相关API
export const userApi = {
  // 登录
  login(data) {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return request({
      url: '/api/auth/login',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  // 获取当前用户信息
  getUserInfo() {
    return request({
      url: '/api/users/me',
      method: 'get'
    })
  },
  // 获取用户列表
  getUserList(params) {
    return request({
      url: '/api/users',
      method: 'get',
      params: params
    })
  },
  // 创建用户
  createUser(data) {
    return request({
      url: '/api/users',
      method: 'post',
      data: data
    })
  },
  // 更新用户
  updateUser(id, data) {
    return request({
      url: `/api/users/${id}`,
      method: 'put',
      data: data
    })
  },
  // 删除用户
  deleteUser(id) {
    return request({
      url: `/api/users/${id}`,
      method: 'delete'
    })
  },
  // 更新当前用户信息
  updateUserInfo(data) {
    return request({
      url: '/api/users/me',
      method: 'put',
      data: data
    })
  },
  // 修改密码
  changePassword(data) {
    return request({
      url: '/api/users/me/password',
      method: 'put',
      data: data
    })
  }
}

// 资产相关API
export const assetApi = {
  // 获取资产列表
  getAssets(params) {
    return request({
      url: '/api/assets',
      method: 'get',
      params: params
    })
  },
  // 创建资产
  createAsset(data) {
    return request({
      url: '/api/assets',
      method: 'post',
      data: data
    })
  },
  // 更新资产
  updateAsset(id, data) {
    return request({
      url: `/api/assets/${id}`,
      method: 'put',
      data: data
    })
  },
  // 删除资产
  deleteAsset(id) {
    return request({
      url: `/api/assets/${id}`,
      method: 'delete'
    })
  }
}

// 报修相关API
export const repairApi = {
  // 获取报修列表
  getRepairList(params) {
    return request({
      url: '/api/repairs',
      method: 'get',
      params: params
    })
  },
  // 创建报修
  createRepair(data) {
    return request({
      url: '/api/repairs',
      method: 'post',
      data: data
    })
  },
  // 更新报修
  updateRepair(id, data) {
    return request({
      url: `/api/repairs/${id}`,
      method: 'put',
      data: data
    })
  }
}

// 公告相关API
export const noticeApi = {
  // 获取公告列表
  getNoticeList(params) {
    return request({
      url: '/api/notices',
      method: 'get',
      params: params
    })
  },
  // 创建公告
  createNotice(data) {
    return request({
      url: '/api/notices',
      method: 'post',
      data: data
    })
  },
  // 更新公告
  updateNotice(id, data) {
    return request({
      url: `/api/notices/${id}`,
      method: 'put',
      data: data
    })
  },
  // 删除公告
  deleteNotice(id) {
    return request({
      url: `/api/notices/${id}`,
      method: 'delete'
    })
  }
}

// 课室相关API
export const classroomApi = {
  // 获取课室列表
  getClassroomList(params) {
    return request({
      url: '/api/classrooms',
      method: 'get',
      params: params
    })
  },
  // 提交课室预约
  submitBooking(data) {
    return request({
      url: '/api/classroom-bookings',
      method: 'post',
      data: data
    })
  },
  // 获取课室详情
  getClassroomDetail(id) {
    return request({
      url: `/api/classrooms/${id}`,
      method: 'get'
    })
  }
}

// 费用相关API
export const financeApi = {
  // 获取费用列表
  getFinanceList(params) {
    return request({
      url: '/api/finances',
      method: 'get',
      params: params
    })
  },
  // 创建费用
  createFinance(data) {
    return request({
      url: '/api/finances',
      method: 'post',
      data: data
    })
  },
  // 更新费用
  updateFinance(id, data) {
    return request({
      url: `/api/finances/${id}`,
      method: 'put',
      data: data
    })
  },
  // 删除费用
  deleteFinance(id) {
    return request({
      url: `/api/finances/${id}`,
      method: 'delete'
    })
  }
}

// 维修管理相关API
export const maintenanceApi = {
  // 获取维修人员列表
  getMaintainers(params) {
    return request({
      url: '/api/users/staff',
      method: 'get',
      params: params
    })
  },
  // 获取维修列表
  getMaintenanceList(params) {
    return request({
      url: '/api/maintenance',
      method: 'get',
      params: params
    })
  },
  // 创建维修任务
  createMaintenance(data) {
    return request({
      url: '/api/maintenance',
      method: 'post',
      data: data
    })
  },
  // 更新维修任务
  updateMaintenance(id, data) {
    return request({
      url: `/api/maintenance/${id}`,
      method: 'put',
      data: data
    })
  },
  // 删除维修任务
  deleteMaintenance(id) {
    return request({
      url: `/api/maintenance/${id}`,
      method: 'delete'
    })
  }
}
