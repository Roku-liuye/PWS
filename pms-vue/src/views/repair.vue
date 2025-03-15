<template>
  <div class="repair-container">
    <div class="repair-header">
      <h2>报修管理</h2>
      <el-button type="primary" @click="handleSubmitRepair">
        <el-icon><Plus /></el-icon>提交报修
      </el-button>
    </div>

    <el-card class="repair-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="报修编号">
          <el-input v-model="queryParams.id" placeholder="请输入报修编号" clearable />
        </el-form-item>
        <el-form-item label="报修类型">
          <el-select style="width: 160px" v-model="queryParams.type" placeholder="请选择报修类型" clearable >
            <el-option label="设备维修" value="equipment" />
            <el-option label="设施维修" value="facility" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select style="width: 160px" v-model="queryParams.status" placeholder="请选择处理状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
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

      <el-table :data="repairList" border style="width: 100%">
        <el-table-column prop="id" label="报修编号" width="120" />
        <el-table-column prop="type" label="报修类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'equipment' ? 'primary' : 'success'">
              {{ scope.row.type === 'equipment' ? '设备维修' : '设施维修' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="报修地点" width="150" />
        <el-table-column prop="description" label="故障描述" show-overflow-tooltip />
        <el-table-column prop="submit_time" label="提交时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.submit_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="处理状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleDetail(scope.row)">
                <el-icon><View /></el-icon>详情
              </el-button>
              <el-button type="primary" link @click="handleProcess(scope.row)" v-if="scope.row.status === 'pending'">
                <el-icon><Loading /></el-icon>处理
              </el-button>
              <el-button type="success" link @click="handleComplete(scope.row)" v-if="scope.row.status === 'processing'">
                <el-icon><Check /></el-icon>完成
              </el-button>
              <el-button type="danger" link @click="handleCancel(scope.row)" v-if="scope.row.status === 'pending'">
                <el-icon><Close /></el-icon>取消
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 提交报修表单对话框 -->
    <el-dialog
      v-model="repairFormVisible"
      title="提交报修"
      width="500px"
      append-to-body
    >
      <el-form ref="repairFormRef" :model="repairForm" :rules="repairRules" label-width="100px">
        <el-form-item label="报修类型" prop="type">
          <el-select v-model="repairForm.type" placeholder="请选择报修类型">
            <el-option label="设备维修" value="equipment" />
            <el-option label="设施维修" value="facility" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="报修地点" prop="location">
          <el-input v-model="repairForm.location" placeholder="请输入报修地点" />
        </el-form-item>
        <el-form-item label="故障描述" prop="description">
          <el-input
            v-model="repairForm.description"
            type="textarea"
            placeholder="请详细描述故障情况"
            :rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="repairFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitRepair">确 定</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 报修详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报修详情"
      width="500px"
      append-to-body
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="报修编号">{{ currentRepair?.id }}</el-descriptions-item>
        <el-descriptions-item label="报修类型">
          <el-tag :type="currentRepair?.type === 'equipment' ? 'primary' : 'success'">
            {{ currentRepair?.type === '设备维修' ? '设备维修' : currentRepair?.type === 'facility' ? '设施维修' : '其他' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报修地点">{{ currentRepair?.location }}</el-descriptions-item>
        <el-descriptions-item label="故障描述">{{ currentRepair?.description }}</el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(currentRepair?.status)">
            {{ getStatusText(currentRepair?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatDateTime(currentRepair?.submit_time) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ currentRepair?.complete_time ? formatDateTime(currentRepair.complete_time) : '未完成' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search, Refresh, View, Close, Check, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '../utils/formatUtils'

// 查询参数
const queryParams = ref({
  id: '',
  type: '',
  status: '',
  page: 1,
  page_size: 10
})

// 报修列表数据
const repairList = ref([])
const total = ref(0)

// 报修表单相关
const repairFormVisible = ref(false)
const repairFormRef = ref()
const repairForm = ref({
  type: '',
  location: '',
  description: ''
})

// 详情对话框相关
const detailDialogVisible = ref(false)
const currentRepair = ref(null)

// 导入API
import { repairApi } from '../api/index.js'


// 获取报修列表数据
const getList = async () => {
  try {
    // 调用后端API获取数据
    const res = await repairApi.getRepairList(queryParams.value)
    repairList.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('获取报修列表失败：', error)
    ElMessage.error('获取报修列表失败')
  }
}

// 搜索
const handleQuery = () => {
  queryParams.value.page = 1
  getList()
}

// 重置
const resetQuery = () => {
  queryParams.value = {
    id: '',
    type: '',
    status: '',
    page: 1,
    page_size: 10
  }
  getList()
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

// 提交报修
const handleSubmitRepair = () => {
  repairForm.value = {
    type: '',
    location: '',
    description: ''
  }
  repairFormVisible.value = true
}

// 查看详情
const handleDetail = (row) => {
  currentRepair.value = row
  detailDialogVisible.value = true
}

// 提交报修表单
const submitRepair = async () => {
  if (!repairFormRef.value) return
  await repairFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await repairApi.createRepair(repairForm.value)
        ElMessage.success('报修提交成功')
        repairFormVisible.value = false
        getList()
        // 重置表单
        repairFormRef.value.resetFields()
      } catch (error) {
        console.error('提交报修失败：', error)
        ElMessage.error('提交报修失败：' + error.message)
      }
    }
  })
}

// 完成报修
const handleComplete = async (row) => {
  try {
    await ElMessageBox.confirm('确认将该报修标记为已完成吗？', '提示', {
      type: 'warning'
    })
    await repairApi.updateRepair(row.id, { 
      status: 'completed',
      complete_time: new Date().toISOString()
    })
    ElMessage.success('报修已完成')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('完成报修失败：', error)
      ElMessage.error('完成报修失败：' + error.message)
    }
  }
}

// 处理报修
const handleProcess = async (row) => {
  try {
    await ElMessageBox.confirm('确认开始处理该报修吗？', '提示', {
      type: 'warning'
    })
    await repairApi.updateRepair(row.id, { status: 'processing' })
    ElMessage.success('已开始处理报修')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更新报修状态失败：', error)
      ElMessage.error('更新报修状态失败：' + error.message)
    }
  }
}

// 取消报修
const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确认取消该报修申请吗？', '提示', {
      type: 'warning'
    })
    await repairApi.updateRepair(row.id, { status: 'cancelled' })
    ElMessage.success('报修已取消')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消报修失败：', error)
      ElMessage.error('取消报修失败：' + error.message)
    }
  }
}

// 分页相关方法
const handleSizeChange = (val) => {
  queryParams.value.page_size = val
  getList()
}

const handleCurrentChange = (val) => {
  queryParams.value.page = val
  getList()
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.repair-container {
  padding: 20px;
}

.repair-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.repair-header h2 {
  margin: 0;
  font-weight: 600;
  font-size: 20px;
}

.repair-content {
  background-color: #fff;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
