<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu
        :default-active="$route.path"
        class="el-menu-vertical"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF">
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/asset">
          <el-icon><Files /></el-icon>
          <span>资产管理</span>
        </el-menu-item>
        <el-menu-item index="/repair">
          <el-icon><Tools /></el-icon>
          <span>报修管理</span>
        </el-menu-item>
        <el-menu-item index="/maintenance">
          <el-icon><Service /></el-icon>
          <span>保修分配</span>
        </el-menu-item>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          <span>费用管理</span>
        </el-menu-item>
        <el-menu-item index="/classroom">
          <el-icon><School /></el-icon>
          <span>租借课室</span>
        </el-menu-item>
        <el-menu-item index="/user">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/notice">
          <el-icon><Bell /></el-icon>
          <span>公告管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header height="60px">
        <div class="header-left">
          <h2>高校物业管理系统</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              {{ userInfo.username || '用户' }}
              <el-icon><CaretBottom /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, Files, Tools, Service, Money, School, User, Bell, CaretBottom } from '@element-plus/icons-vue'
import { userApi } from '../api/index'

const router = useRouter()
const userInfo = ref({})

// 获取用户信息
const getUserInfo = async () => {
  try {
    const res = await userApi.getUserInfo()
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'changePassword':
      router.push('/change-password')
      break
    case 'logout':
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.success('退出成功')
      break
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>