<template>
  <div class="login-container" >
    <el-card class="login-card">
      <div class="login-header">
        <h2>高校物业管理系统</h2>
        <p>用户登录</p>
      </div>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="0" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-button" @click="handleLogin">登录</el-button>
        </el-form-item>
        <div class="register-link">
          <span>没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { userApi } from '../api/index'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        const res = await userApi.login(loginForm)
        localStorage.setItem('token', res.access_token)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  margin: 0 auto;
  align-items: center;
  height: 100vh;
  background-color: #f4f7fa; /* 与主界面背景色保持一致 */
}

.login-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 增强阴影效果 */
  transition: box-shadow 0.3s;
}

.login-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 16px;
  color: #606266;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
  height: 40px; /* 增加按钮高度 */
  font-size: 16px; /* 增加字体大小 */
  background-color: #409EFF; /* 与主界面按钮颜色保持一致 */
  border-color: #409EFF;
  transition: all 0.3s;
}

.login-button:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.register-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}

.register-link a {
  color: #409eff;
  margin-left: 5px;
}
</style>