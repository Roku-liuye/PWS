<template>
  <div class="home-container">
    <!-- 系统公告 -->
    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>系统公告</span>
        </div>
      </template>
      <div class="notice-list">
        <div v-for="notice in notices" :key="notice.id" class="notice-item" @click="showNoticeDetail(notice)">
          <div class="notice-main">
            <div class="notice-title">
              <el-icon><Bell /></el-icon>
              <span>{{ notice.title }}</span>
            </div>
            <div class="notice-info">
              <span class="notice-publisher_id">发布人：{{ notice.publisher_name || notice.publisher_id }}</span>
              <span class="notice-time">{{ notice.publish_time }}</span>
            </div>
          </div>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- 公告详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="公告详情"
      width="50%"
      :before-close="handleDialogClose"
    >
      <div class="notice-detail" v-if="currentNotice">
        <h3>{{ currentNotice.title }}</h3>
        <div class="notice-meta">
          <span>发布人：{{ currentNotice.publisher_name }}</span>
          <span>发布时间：{{ currentNotice.publish_time }}</span>
        </div>
        <div class="notice-content">
          {{ currentNotice.content }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bell, ArrowRight } from '@element-plus/icons-vue'
import { noticeApi, userApi } from '../api/index'

// 教室使用率数据
const classroomUsage = ref(0)

// 进度条颜色
const progressColor = computed(() => {
  const usage = classroomUsage.value
  if (usage < 60) return '#67c23a'
  if (usage < 80) return '#e6a23c'
  return '#f56c6c'
})

// 公告数据
const notices = ref([])
const dialogVisible = ref(false)
const currentNotice = ref(null)

// 显示公告详情
const showNoticeDetail = (notice) => {
  currentNotice.value = notice
  dialogVisible.value = true
}

// 关闭对话框
const handleDialogClose = () => {
  dialogVisible.value = false
  currentNotice.value = null
}

// 获取公告列表
const getNoticeList = async () => {
  try {
    const res = await noticeApi.getNoticeList()
    const noticeItems = res.items || []
    
    // 获取所有不重复的发布人ID
    const publisherIds = [...new Set(noticeItems.map(notice => notice.publisher_id))]
    
    // 批量获取用户信息
    const { items: users } = await userApi.getUserList()
    
    // 创建用户ID到真实姓名的映射
    const userMap = {}
    users.forEach(user => {
      if (user && user.id) {
        userMap[user.id] = user.real_name
      }
    })
    
    // 更新公告列表，添加发布人真实姓名
    notices.value = noticeItems.map(notice => ({
      ...notice,
      publisher_name: userMap[notice.publisher_id] || notice.publisher_id
    }))
  } catch (error) {
    console.error('获取公告列表失败：', error)
  }
}

// 获取数据
const getData = async () => {
  try {
    await getNoticeList()
  } catch (error) {
    console.error('获取数据失败：', error)
  }
}

onMounted(() => {
  getData()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.usage-card {
  height: 340px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.usage-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 250px;
}

.percentage-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.percentage-label {
  display: block;
  font-size: 14px;
  color: #909399;
}

.mt-4 {
  margin-top: 20px;
}

.notice-list {
  .notice-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #ebeef5;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background-color: #f5f7fa;
    }

    &:last-child {
      border-bottom: none;
    }
  }

  .notice-main {
    flex: 1;
  }

  .notice-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #303133;
    margin-bottom: 8px;

    .el-icon {
      color: #409eff;
    }
  }

  .notice-info {
    display: flex;
    gap: 16px;
    font-size: 13px;
    color: #909399;
  }
}

.notice-detail {
  h3 {
    margin: 0 0 16px 0;
    color: #303133;
  }

  .notice-meta {
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    font-size: 14px;
    color: #909399;
  }

  .notice-content {
    font-size: 14px;
    line-height: 1.6;
    color: #606266;
  }
}
</style>