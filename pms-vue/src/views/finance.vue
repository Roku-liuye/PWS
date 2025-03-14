<template>
  <div class="finance-container">
    <div class="finance-header">
      <h2>费用管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增费用
      </el-button>
    </div>

    <el-card class="finance-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="费用类型">
          <el-select style="min-width: 160px" v-model="queryParams.type" placeholder="请选择费用类型" clearable>
            <el-option label="设备采购" value="purchase" />
            <el-option label="维修费用" value="repair" />
            <el-option label="能源消耗" value="energy" />
            <el-option label="其他支出" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="queryParams.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
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

      <!-- 费用统计卡片 -->
      <div class="statistics-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>总支出</span>
                  <el-tag type="danger">本月</el-tag>
                </div>
              </template>
              <div class="card-amount">¥ {{ statistics.totalAmount }}</div>
            </el-card>
          </el-col>
          <el-col :span="6" v-for="(item, index) in statistics.typeAmount" :key="index">
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>{{ item.name }}</span>
                  <el-tag>本月</el-tag>
                </div>
              </template>
              <div class="card-amount">¥ {{ item.amount }}</div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-table :data="financeList" border style="width: 100%">
        <el-table-column prop="id" label="费用编号" width="120" />
        <el-table-column prop="type" label="费用类型" width="120">
          <template #default="scope">
            <el-tag :type="getTypeTag(scope.row.type)">
              {{ getTypeText(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span class="amount">¥ {{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="费用说明" show-overflow-tooltip />
        <el-table-column prop="createTime" label="记录时间" width="160" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>编辑
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

    <!-- 费用表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增费用' : '编辑费用'"
      width="500px"
      append-to-body
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="费用类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择费用类型">
            <el-option label="设备采购" value="purchase" />
            <el-option label="维修费用" value="repair" />
            <el-option label="能源消耗" value="energy" />
            <el-option label="其他支出" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :precision="2"
            :step="100"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入费用说明"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitForm">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 查询参数
const queryParams = ref({
  type: '',
  dateRange: [],
  pageNum: 1,
  pageSize: 10
})

// 费用统计数据
const statistics = ref({
  totalAmount: '50,000.00',
  typeAmount: [
    { name: '设备采购', amount: '20,000.00' },
    { name: '维修费用', amount: '15,000.00' },
    { name: '能源消耗', amount: '15,000.00' }
  ]
})

// 费用列表数据
const financeList = ref([])
const total = ref(0)

// 导入API
import { financeApi } from '../api/index.js'

// 获取费用列表数据
const getList = async () => {
  try {
    // 处理日期范围参数
    let params = { ...queryParams.value }
    if (params.dateRange && params.dateRange.length === 2) {
      params.start_date = params.dateRange[0]
      params.end_date = params.dateRange[1]
      delete params.dateRange
    }
    
    // 调用后端API获取数据
    const res = await financeApi.getFinanceList(params)
    financeList.value = res.items || []
    total.value = res.total || 0
    
    // 更新统计数据 (这部分可能需要单独的API调用)
    // TODO: 实现费用统计的API调用
  } catch (error) {
    console.error('获取费用列表失败：', error)
    ElMessage.error('获取费用列表失败')
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
    type: '',
    dateRange: [],
    pageNum: 1,
    pageSize: 10
  }
  getList()
}

// 获取费用类型标签
const getTypeTag = (type) => {
  const typeMap = {
    purchase: 'danger',
    repair: 'warning',
    maintenance: 'warning',
    energy: 'success',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

// 获取费用类型文本
const getTypeText = (type) => {
  const typeMap = {
    purchase: '设备采购',
    repair: '维修费用',
    maintenance: '维护费用',
    energy: '能源消耗',
    other: '其他支出'
  }
  return typeMap[type] || '未知'
}

// 表单相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref()
const form = ref({
  type: '',
  amount: 0,
  description: ''
})

const rules = {
  type: [{ required: true, message: '请选择费用类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入费用金额', trigger: 'blur' }],
  description: [{ required: true, message: '请输入费用说明', trigger: 'blur' }]
}

// 新增费用
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    type: '',
    amount: 0,
    description: ''
  }
  dialogVisible.value = true
}

// 编辑费用
const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = { ...row }
  dialogVisible.value = true
}

// 删除费用
const handleDelete = (row) => {
  ElMessageBox.confirm('确认要删除该费用记录吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await financeApi.deleteFinance(row.id)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      console.error('删除费用记录失败：', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 提交表单
const submitForm = () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          await financeApi.createFinance(form.value)
          ElMessage.success('新增成功')
        } else {
          await financeApi.updateFinance(form.value.id, form.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        console.error('提交费用记录失败：', error)
        ElMessage.error('提交失败')
      }
    }
  })
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
.finance-container {
  padding: 20px;
}

.finance-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.statistics-cards {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-amount {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.amount {
  color: #f56c6c;
  font-weight: bold;
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