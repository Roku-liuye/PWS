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
          <el-select v-model="queryParams.role" placeholder="请选择角色" clearable>
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
        <el-table-column prop="id" label="用户ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ getRoleText(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="primary" link @click="handleResetPwd(scope.row)">
                <el-icon><Key /></el-icon>重置密码
              </el-button>
              <el-button :type="scope.row.status === 'active' ? 'danger' : 'success'" link @click="handleToggleStatus(scope.row)">
                <el-icon><CircleClose v-if="scope.row.status === 'active'" /><CircleCheck v-else /></el-icon>
                {{ scope.row.status === 'active' ? '禁用' : '启用' }}
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Search, Refresh, Key, CircleClose, CircleCheck } from '@element-plus/icons-vue'
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

// 新增用户
const handleAdd = () => {
  // TODO: 实现新增用户功能
  console.log('新增用户')
}

// 编辑用户
const handleEdit = (row) => {
  // TODO: 实现编辑用户功能
  console.log('编辑用户：', row)
}

// 重置密码
const handleResetPwd = (row) => {
  ElMessageBox.confirm(`确认重置用户"${row.username}"的密码吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // TODO: 调用后端API重置密码
      // await userApi.resetPassword(row.id)
      ElMessage.success('密码重置成功')
    } catch (error) {
      console.error('密码重置失败：', error)
      ElMessage.error('密码重置失败')
    }
  }).catch(() => {})
}

// 切换用户状态
const handleToggleStatus = (row) => {
  const action = row.status === 'active' ? '禁用' : '启用'
  ElMessageBox.confirm(`确认${action}用户"${row.username}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // TODO: 调用后端API修改用户状态
      // await userApi.updateUser(row.id, { status: row.status === 'active' ? 'inactive' : 'active' })
      ElMessage.success(`${action}成功`)
    } catch (error) {
      console.error(`${action}用户失败：`, error)
      ElMessage.error(`${action}失败`)
    }
  }).catch(() => {})
}

// 分页大小改变
const handleSizeChange = (val) => {
  queryParams.value.pageSize = val
  handleQuery()
}

// 当前页改变
const handleCurrentChange = (val) => {
  queryParams.value.pageNum = val
  handleQuery()
}

onMounted(() => {
  handleQuery()
})
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