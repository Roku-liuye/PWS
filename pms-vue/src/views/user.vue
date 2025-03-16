<template>
  <div class="user-container">
    <div class="user-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增用户
      </el-button>
    </div>

    <el-card class="user-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="queryParams.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select style="min-width: 160px" v-model="queryParams.role" placeholder="请选择角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="维修人员" value="maintainer" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>

      <el-table :data="userList" border style="width: 100%">
        <el-table-column prop="id" label="用户ID" min-width="20" />
        <el-table-column prop="username" label="用户名" min-width="30" />
        <el-table-column prop="real_name" label="姓名" min-width="40" />
        <el-table-column prop="role" label="角色" min-width="20">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ getRoleText(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" min-width="60" />
        <el-table-column prop="email" label="邮箱" min-width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="primary" link @click="handleResetPwd(scope.row)">
                <el-icon><Key /></el-icon>重置密码
              </el-button>
              <el-button type="danger" link @click="handleDelete(scope.row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.pageNum"
          v-model:page-size="queryParams.pageSize"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @close="resetForm">
      <el-form ref="userFormRef" :model="userForm" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="维修人员" value="staff" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="userForm.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Search, Refresh, Key, Delete, CircleClose, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 查询参数
const queryParams = ref({
  username: '',
  role: '',
  pageNum: 1,
  pageSize: 10
})

// 用户列表数据
const userList = ref([])
const total = ref(0)

// 获取角色类型对应的Tag类型
const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    staff: 'warning',
    teacher: 'warning',
    student: 'info'
  }
  return types[role] || 'info'
}

// 获取角色文本
const getRoleText = (role) => {
  const texts = {
    admin: '管理员',
    staff: '维修人员',
    teacher: '教师',
    student: '学生'
  }
  return texts[role] || '未知'
}

// 导入API
import { userApi } from '../api/index.js'

// 删除用户处理函数
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要永久删除用户 ${row.username} 吗?`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.deleteUser(row.id)
      ElMessage.success('删除用户成功')
      handleQuery()
    } catch (error) {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }).catch(() => {})
}

// 查询用户列表
const handleQuery = async () => {
  try {
    const res = await userApi.getUserList(queryParams.value)
    userList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取用户列表失败：', error)
    ElMessage.error('获取用户列表失败')
  }
}

// 重置查询条件
const resetQuery = () => {
  queryParams.value = {
    username: '',
    role: '',
    pageNum: 1,
    pageSize: 10
  }
  handleQuery()
}

// 对话框相关数据
const dialogVisible = ref(false)
const dialogTitle = ref('')
const userFormRef = ref()
const userForm = ref({
  username: '',
  password: '',
  role: '',
  real_name: '',
  phone: '',
  email: ''
})

// 在组件挂载时获取用户列表
onMounted(() => {
  handleQuery()
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  real_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 重置表单
const resetForm = () => {
  userFormRef.value?.resetFields()
  userForm.value = {
    username: '',
    password: '',
    role: '',
    real_name: '',
    phone: '',
    email: ''
  }
}

// 编辑用户
const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  userForm.value = { ...row }
  dialogVisible.value = true
}

// 新增用户
const handleAdd = () => {
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

const handleResetPwd = (row) => {
  ElMessageBox.confirm(`确定要重置 ${row.username} 的密码吗?`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await userApi.updateUser(row.id, { password: '123456' })
      ElMessage.success('密码已重置为123456')
      handleQuery()
    } catch (error) {
      ElMessage.error('重置失败: ' + (error.message || '未知错误'))
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = async () => {
  if (!userFormRef.value) return
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogTitle.value === '新增用户') {
          await userApi.createUser(userForm.value)
          ElMessage.success('新增用户成功')
        } else {
          await userApi.updateUser(userForm.value.id, userForm.value)
          ElMessage.success('更新用户成功')
        }
        dialogVisible.value = false
        handleQuery()
      } catch (error) {
        console.error('操作失败：', error)
        ElMessage.error('操作失败：' + (error.message || '未知错误'))
      }
    }
  })
}
</script>

<style scoped>
.user-container {
  padding: 20px;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-content {
  background-color: #fff;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>