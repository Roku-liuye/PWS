<template>
  <div class="maintenance-container">
    <div class="maintenance-header">
      <h2>保修分配管理</h2>
    </div>

    <el-card class="maintenance-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="报修编号">
          <el-input v-model="queryParams.repairNo" placeholder="请输入报修编号" clearable />
        </el-form-item>
        <el-form-item label="维修状态">
          <el-select v-model="queryParams.status" placeholder="请选择维修状态" clearable>
            <el-option label="待分配" value="unassigned" />
            <el-option label="已分配" value="assigned" />
            <el-option label="维修中" value="processing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="维修人员">
          <el-select v-model="queryParams.maintainer" placeholder="请选择维修人员" clearable>
            <el-option label="张三" value="zhangsan" />
            <el-option label="李四" value="lisi" />
            <el-option label="王五" value="wangwu" />
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
        <el-table-column prop="repairNo" label="报修编号" width="120" />
        <el-table-column prop="type" label="报修类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'equipment' ? 'primary' : 'success'">
              {{ scope.row.type === 'equipment' ? '设备维修' : '设施维修' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="报修地点" width="150" />
        <el-table-column prop="description" label="故障描述" show-overflow-tooltip />
        <el-table-column prop="submitTime" label="提交时间" width="160" />
        <el-table-column prop="status" label="维修状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maintainer" label="维修人员" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleAssign(scope.row)" v-if="scope.row.status === 'unassigned'">
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

    <!-- 分配维修人员对话框 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="分配维修人员"
      width="400px"
      append-to-body
    >
      <el-form ref="assignFormRef" :model="assignForm" :rules="assignRules" label-width="100px">
        <el-form-item label="维修人员" prop="maintainer">
          <el-select v-model="assignForm.maintainer" placeholder="请选择维修人员">
            <el-option label="张三" value="zhangsan" />
            <el-option label="李四" value="lisi" />
            <el-option label="王五" value="wangwu" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="assignForm.remark"
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

// 查询参数
const queryParams = ref({
  repairNo: '',
  status: '',
  maintainer: '',
  pageNum: 1,
  pageSize: 10
})

// 维修列表数据
const maintenanceList = ref([])
const total = ref(0)

// 获取维修列表数据
const getList = async () => {
  try {
    // TODO: 调用后端API获取数据
    // const { data } = await getMaintenanceList(queryParams.value)
    // maintenanceList.value = data.list
    // total.value = data.total

    // 模拟数据
    maintenanceList.value = [
      {
        repairNo: 'R2024001',
        type: 'equipment',
        location: '教学楼A101',
        description: '投影仪无法开机',
        submitTime: '2024-01-10 14:30:00',
        status: 'unassigned',
        maintainer: '-'
      }
    ]
    total.value = 1
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
    repairNo: '',
    status: '',
    maintainer: '',
    pageNum: 1,
    pageSize: 10
  }
  getList()
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    unassigned: 'info',
    assigned: 'warning',
    processing: 'primary',
    completed: 'success'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    unassigned: '待分配',
    assigned: '已分配',
    processing: '维修中',
    completed: '已完成'
  }
  return statusMap[status] || '未知'
}

// 分配维修人员
const assignDialogVisible = ref(false)
const assignFormRef = ref()
const assignForm = ref({
  repairNo: '',
  maintainer: '',
  remark: ''
})

const assignRules = {
  maintainer: [{ required: true, message: '请选择维修人员', trigger: 'change' }]
}

const handleAssign = (row) => {
  assignForm.value = {
    repairNo: row.repairNo,
    maintainer: '',
    remark: ''
  }
  assignDialogVisible.value = true
}

const submitAssign = async () => {
  if (!assignFormRef.value) return
  await assignFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: 调用后端API分配维修人员
        // await assignMaintainer(assignForm.value)
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
      // TODO: 调用后端API完成维修
      // await completeMaintenance(row.repairNo)
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
  ElMessage('查看维修详情：' + row.repairNo)
}

// 分页
const handleSizeChange = (val) => {
  queryParams.value.pageSize = val
  getList()
}

const handleCurrentChange = (val) => {
  queryParams.value.pageNum = val
  getList()
}

onMounted(() => {
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