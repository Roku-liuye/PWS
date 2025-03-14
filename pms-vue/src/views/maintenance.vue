<template>
  <div class="maintenance-container">
    <div class="maintenance-header">
      <h2>保修分配管理</h2>
    </div>

    <el-card class="maintenance-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="报修编号">
          <el-input v-model="queryParams.id" placeholder="请输入报修编号" clearable />
        </el-form-item>
        <el-form-item label="维修状态">
          <el-select style="min-width: 160px" v-model="queryParams.status" placeholder="请选择维修状态" clearable>
            <el-option label="待分配" value="pending" />
            <el-option label="维修中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item style="min-width: 160px" label="维修人员">
          <el-select v-model="queryParams.maintainer" placeholder="请选择维修人员" clearable>
            <el-option
              v-for="maintainer in maintainerList"
              :key="maintainer.id"
              :label="maintainer.real_name"
              :value="maintainer.id"
            />
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

      <el-table :data="maintenanceList" border style="width: 100%">
        <el-table-column prop="id" label="报修编号" width="120" />
        <el-table-column prop="repair_id" label="报修编号" width="120" />
        <el-table-column prop="assign_time" label="分配时间" width="160" />
        <el-table-column prop="expected_time" label="预计完成时间" width="160" />
        <el-table-column prop="actual_time" label="实际完成时间" width="160" />
        <el-table-column prop="result" label="维修结果" show-overflow-tooltip />
        <el-table-column prop="assign_time" label="分配时间" width="160" />
        <el-table-column prop="expected_time" label="预计完成时间" width="160" />
        <el-table-column prop="status" label="维修状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maintainer_name" label="维修人员" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleAssign(scope.row)" v-if="scope.row.status === 'pending'">
                <el-icon><UserFilled /></el-icon>分配
              </el-button>
              <el-button type="success" link @click="handleComplete(scope.row)" v-if="scope.row.status === 'processing'">
                <el-icon><Select /></el-icon>完成
              </el-button>
              <el-button type="primary" link @click="handleDetail(scope.row)">
                <el-icon><View /></el-icon>详情
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

    <!-- 分配维修人员对话框 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="分配维修人员"
      width="400px"
      append-to-body
    >
      <el-form ref="assignFormRef" :model="assignForm" :rules="assignRules" label-width="100px">
        <el-form-item label="维修人员" prop="maintainer_id">
          <el-select v-model="assignForm.maintainer_id" placeholder="请选择维修人员">
            <el-option
              v-for="maintainer in maintainerList"
              :key="maintainer.id"
              :label="maintainer.real_name"
              :value="maintainer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预计完成时间" prop="expected_time">
          <el-date-picker
            v-model="assignForm.expected_time"
            type="datetime"
            placeholder="请选择预计完成时间"
          />
        </el-form-item>
        <el-form-item label="备注" prop="result">
          <el-input
            v-model="assignForm.result"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="assignDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitAssign">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Refresh, View, UserFilled, Select } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { maintenanceApi } from '../api/index.js'

// 查询参数
const queryParams = ref({
  id: '',
  status: '',
  maintainer_id: '',
  page: 1,
  page_size: 10
})

// 维修列表数据
const maintenanceList = ref([])
const total = ref(0)
const maintainerList = ref([])

// 获取维修人员列表
const getMaintainers = async () => {
  try {
    const res = await maintenanceApi.getMaintainers({ role: 'staff' })
    maintainerList.value = res.items
  } catch (error) {
    console.error('获取维修人员列表失败：', error)
    ElMessage.error('获取维修人员列表失败')
  }
}

// 获取维修列表数据
const getList = async () => {
  try {
    const res = await maintenanceApi.getMaintenanceList(queryParams.value)
    if (res && res.items) {
      maintenanceList.value = res.items.map(item => ({
        ...item,
        maintainer_name: maintainerList.value.find(m => m.id === item.maintainer_id)?.real_name || '未分配'
      }))
      total.value = res.total
    } else {
      maintenanceList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取维修列表失败：', error)
    ElMessage.error('获取维修列表失败')
  }
}

// 搜索
const handleQuery = () => {
  queryParams.value.pageNum = 1
  getList()
}

// 重置
const resetQuery = () => {
  queryParams.value = {
    id: '',
    status: '',
    maintainer_id: '',
    page: 1,
    page_size: 10
  }
  getList()
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '待分配',
    processing: '维修中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 分配对话框
const assignDialogVisible = ref(false)
const assignFormRef = ref()
const assignForm = ref({
  id: '',
  maintainer_id: '',
  expected_time: '',
  result: ''
})

// 分配表单验证规则
const assignRules = {
  maintainer_id: [{ required: true, message: '请选择维修人员', trigger: 'change' }],
  expected_time: [{ required: true, message: '请选择预计完成时间', trigger: 'change' }]
}

// 打开分配对话框
const handleAssign = (row) => {
  assignForm.value.id = row.id
  assignDialogVisible.value = true
}

// 提交分配
const submitAssign = async () => {
  await assignFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.post('/api/maintenance', assignForm.value)
        ElMessage.success('分配成功')
        assignDialogVisible.value = false
        getList()
      } catch (error) {
        console.error('分配维修人员失败：', error)
        ElMessage.error('分配失败')
      }
    }
  })
}

// 完成维修
const handleComplete = (row) => {
  ElMessageBox.confirm('确认该维修任务已完成？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await axios.put(`/api/maintenance/${row.id}`, {
        status: 'completed',
        actual_time: new Date().toISOString()
      })
      ElMessage.success('操作成功')
      getList()
    } catch (error) {
      console.error('完成维修失败：', error)
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

// 查看详情
const handleDetail = (row) => {
  ElMessage('查看维修详情：' + row.id)
}

// 分页
const handleSizeChange = (val) => {
  queryParams.value.page_size = val
  getList()
}

const handleCurrentChange = (val) => {
  queryParams.value.page = val
  getList()
}

onMounted(() => {
  getMaintainers()
  getList()
})
</script>

<style scoped>
.maintenance-container {
  padding: 20px;
}

.maintenance-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  text-align: right;
}
</style>