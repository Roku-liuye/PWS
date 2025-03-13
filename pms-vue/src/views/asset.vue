<template>
  <div class="asset-container">
    <div class="asset-header">
      <h2>资产管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增资产
      </el-button>
    </div>

    <el-card class="asset-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="资产名称">
          <el-input v-model="queryParams.name" placeholder="请输入资产名称" clearable />
        </el-form-item>
        <el-form-item label="资产类型">

          <el-select style="width: 160px" v-model="queryParams.type" placeholder="请选择资产类型" clearable>
            <el-option v-for="type in assetTypes" :key="type" :label="type" :value="type"></el-option>
          </el-select>

        </el-form-item>
        <el-form-item label="使用状态">

          <el-select 
            style="width: 160px" 
            v-model="queryParams.status" 
            placeholder="请选择使用状态" 
            clearable
          >
            <el-option 
              v-for="status in assetStatus" 
              :key="status.value" 
              :label="status.label" 
              :value="status.value"
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

      <el-table :data="assetList" border style="width: 100%" :fit="true">
        <el-table-column prop="id" label="资产编号" min-width="80" />
        <el-table-column prop="name" label="资产名称" min-width="120" />
        <el-table-column prop="type" label="资产类型" min-width="100" />
        <el-table-column prop="location" label="存放位置" min-width="120" />
        <el-table-column prop="purchase_date" label="购入日期" min-width="100">
          <template #default="scope">
            {{ formatDate(scope.row.purchase_date) }}
          </template>
        </el-table-column>
         
        <el-table-column prop="status" label="使用状态" min-width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ assetStatus.find(s => s.value === scope.row.status)?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="120" fixed="right">
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
          v-model:currentPage="queryParams.page"
          v-model:pageSize="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑资产对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '新增资产' : '编辑资产'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="assetForm" label-width="100px" ref="assetFormRef" :rules="rules">
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="assetForm.name" />
        </el-form-item>
        <el-form-item label="资产类型" prop="type">
          <el-select v-model="assetForm.type" placeholder="请选择资产类型" style="width: 100%">
            <el-option v-for="type in assetTypes" :key="type" :label="type" :value="type" />
          </el-select>
        </el-form-item>
        <el-form-item label="存放位置" prop="location">
          <el-input v-model="assetForm.location" />
        </el-form-item>
        <el-form-item label="使用状态" prop="status">
          <el-select v-model="assetForm.status" placeholder="请选择使用状态" style="width: 100%">
            <el-option 
              v-for="status in assetStatus" 
              :key="status.value" 
              :label="status.label" 
              :value="status.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="购入日期" prop="purchase_date">
          <el-date-picker v-model="assetForm.purchase_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="assetForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetApi } from '../api'

// 资产类型和状态选项
const assetTypes = ['教学设备', '办公设备', '实验设备', '体育器材', '其他']
const assetStatus = [
  { label: '正常', value: 'normal' },
  { label: '维修中', value: 'repair' },
  { label: '报废', value: 'scrapped' }
]

// 查询参数
const queryParams = reactive({
  name: '',
  type: '',
  status: '',
  page: 1,
  page_size: 10
})

// 资产列表数据
const assetList = ref([])
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')
const assetFormRef = ref(null)
const assetForm = reactive({
  name: '',
  type: '',
  location: '',
  status: 'normal',
  purchase_date: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入存放位置', trigger: 'blur' }],
  status: [{ required: true, message: '请选择使用状态', trigger: 'change' }]
}

// 获取资产列表数据
const getList = async () => {
  try {
    const params = {
      search: queryParams.name || undefined,
      type: queryParams.type || undefined,
      status: queryParams.status || undefined,
      page: queryParams.page,
      page_size: queryParams.page_size
    }
    const res = await assetApi.getAssets(params)
    assetList.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('获取资产列表失败：', error)
    ElMessage.error('获取资产列表失败')
  }
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getList()
}

// 重置
const resetQuery = () => {
  queryParams.name = ''
  queryParams.type = ''
  queryParams.status = ''
  queryParams.page = 1
  getList()
}

// 新增资产
const handleAdd = () => {
  dialogType.value = 'add'
  assetForm.id = undefined
  assetForm.name = ''
  assetForm.type = ''
  assetForm.location = ''
  assetForm.status = 'normal'
  assetForm.purchase_date = ''
  assetForm.description = ''
  dialogVisible.value = true
  // 在下一个事件循环中重置表单验证
  setTimeout(() => {
    if (assetFormRef.value) {
      assetFormRef.value.resetFields()
    }
  }, 0)
}

// 编辑资产
const handleEdit = (row) => {
  dialogType.value = 'edit'
  // 使用深拷贝避免直接修改列表数据
  assetForm.id = row.id
  assetForm.name = row.name
  assetForm.type = row.type
  assetForm.location = row.location
  assetForm.status = row.status
  assetForm.purchase_date = row.purchase_date
  assetForm.description = row.description
  dialogVisible.value = true
  // 在下一个事件循环中重置表单验证
  setTimeout(() => {
    if (assetFormRef.value) {
      assetFormRef.value.clearValidate()
    }
  }, 0)
}

// 删除资产
const handleDelete = (row) => {
  ElMessageBox.confirm('确认要删除该资产吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await assetApi.deleteAsset(row.id)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      console.error('删除资产失败：', error)
      ElMessage.error(error.message || '删除失败')
    }
  }).catch(() => {})
}

// 提交表单
const handleSubmit = async () => {
  if (!assetFormRef.value) return
  
  try {
    await assetFormRef.value.validate()
    
    // 准备提交的数据
    const submitData = {
      name: assetForm.name,
      type: assetForm.type,
      status: assetForm.status,
      location: assetForm.location,
      description: assetForm.description
    }
    
    // 如果有日期，添加到提交数据中
    if (assetForm.purchase_date) {
      submitData.purchase_date = new Date(assetForm.purchase_date)
    }
    
    if (dialogType.value === 'add') {
      await assetApi.createAsset(submitData)
      ElMessage.success('添加成功')
    } else {
      await assetApi.updateAsset(assetForm.id, submitData)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    getList()
  } catch (error) {
    console.error('操作失败：', error)
    ElMessage.error(error.message || '操作失败')
  }
}

// 分页
const handleSizeChange = (val) => {
  queryParams.page_size = val
  getList()
}

const handleCurrentChange = (val) => {
  queryParams.page = val
  getList()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

// 获取状态标签类型
const getStatusType = (status) => {
  switch (status) {
    case 'normal':
      return 'success'
    case 'repair':
      return 'warning'
    case 'scrapped':
      return 'danger'
    default:
      return 'info'
  }
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.asset-container {
  padding: 20px;
}

.asset-header {
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
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.asset-content {
  width: 100%;
}
</style>