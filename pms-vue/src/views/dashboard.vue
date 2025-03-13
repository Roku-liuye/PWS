<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6" v-for="(item, index) in statistics" :key="index">
        <el-card shadow="hover" class="statistics-card">
          <template #header>
            <div class="card-header">
              <span>{{ item.title }}</span>
              <el-tag>{{ item.tag }}</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="card-value">{{ item.value }}</div>
            <div class="card-label">{{ item.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <!-- 待处理事项 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理报修</span>
              <el-button text>查看全部</el-button>
            </div>
          </template>
          <el-table :data="pendingRepairs" style="width: 100%">
            <el-table-column prop="repairNo" label="报修编号" width="120" />
            <el-table-column prop="type" label="报修类型" width="100">
              <template #default="scope">
                <el-tag size="small" :type="scope.row.type === 'equipment' ? 'primary' : 'success'">
                  {{ scope.row.type === 'equipment' ? '设备维修' : '设施维修' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="报修地点" />
            <el-table-column prop="submitTime" label="提交时间" width="160" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 系统公告 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统公告</span>
              <el-button text>查看全部</el-button>
            </div>
          </template>
          <div class="notice-list">
            <div v-for="(notice, index) in notices" :key="index" class="notice-item">
              <div class="notice-title">
                <el-icon><Bell /></el-icon>
                <span>{{ notice.title }}</span>
              </div>
              <div class="notice-time">{{ notice.time }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'

// 统计数据
const statistics = ref([
  { title: '资产总数', value: '358', label: '件', tag: '总计' },
  { title: '待处理报修', value: '12', label: '件', tag: '本周' },
  { title: '本月费用', value: '￥45,890', label: '元', tag: '本月' },
  { title: '课室使用率', value: '85%', label: '当前', tag: '实时' }
])

// 待处理报修列表
const pendingRepairs = ref([
  {
    repairNo: 'R2024001',
    type: 'equipment',
    location: '教学楼A101',
    submitTime: '2024-01-10 14:30:00'
  },
  {
    repairNo: 'R2024002',
    type: 'facility',
    location: '图书馆阅览室',
    submitTime: '2024-01-10 15:20:00'
  }
])

// 系统公告列表
const notices = ref([
  {
    title: '教学楼A栋空调系统维护通知',
    time: '2024-01-10 10:00'
  },
  {
    title: '寒假期间宿舍水电费充值通知',
    time: '2024-01-09 16:30'
  },
  {
    title: '图书馆阅览室座椅更换通知',
    time: '2024-01-08 14:20'
  }
])

// 获取数据
const getData = async () => {
  try {
    // TODO: 调用后端API获取数据
    // const { data } = await getDashboardData()
    // statistics.value = data.statistics
    // pendingRepairs.value = data.pendingRepairs
    // notices.value = data.notices
  } catch (error) {
    console.error('获取数据失败：', error)
  }
}

onMounted(() => {
  getData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.statistics-card {
  height: 180px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.card-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 10px;
}

.card-label {
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
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .notice-title {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #303133;

      .el-icon {
        color: #409eff;
      }
    }

    .notice-time {
      color: #909399;
      font-size: 13px;
    }
  }
}
</style>