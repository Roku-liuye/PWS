<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h3>个人信息</h3>
          <el-button type="primary" @click="handleEdit" v-if="!isEditing">编辑</el-button>
          <div v-else>
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button @click="handleCancel">取消</el-button>
          </div>
        </div>
      </template>

      <el-form :model="userForm" :disabled="!isEditing" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-input v-model="userForm.role" disabled />
        </el-form-item>
        <el-form-item label="手机号码">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '../api/index'

const isEditing = ref(false)
const userForm = reactive({
  username: '',
  real_name: '',
  role: '',
  phone: '',
  email: ''
})

// 获取用户信息
const getUserInfo = async () => {
  try {
    const userData = await userApi.getUserInfo()
    Object.assign(userForm, userData)
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 编辑信息
const handleEdit = () => {
  isEditing.value = true
}

// 保存信息
const handleSave = async () => {
  try {
    await userApi.updateUserInfo(userForm)
    ElMessage.success('保存成功')
    isEditing.value = false
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 取消编辑
const handleCancel = () => {
  isEditing.value = false
  getUserInfo() // 重新获取用户信息，恢复原始数据
}

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}
</style>