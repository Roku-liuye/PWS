<template>
  <div class="notice-container">
    <div class="notice-header">
      <h2>公告管理</h2>
      <el-button type="primary" @click="handlePublish">
        <el-icon><Plus /></el-icon>发布公告
      </el-button>
    </div>

    <el-card class="notice-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="标题">
          <el-input v-model="queryParams.title" placeholder="请输入公告标题" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select style="min-width: 160px" v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
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

      <el-table :data="noticeList" border style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column prop="publisher_id" label="发布人" width="120" />
        <el-table-column prop="publish_time" label="发布时间" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.publish_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'published' ? 'success' : 'info'">
              {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button type="primary" link @click="handleView(scope.row)">
                <el-icon><View /></el-icon>查看
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

    <!-- 公告对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="50%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="noticeFormRef"
        :model="noticeForm"
        :rules="noticeRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="noticeForm.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="noticeForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="noticeForm.status">
            <el-radio label="published">发布</el-radio>
            <el-radio label="draft">草稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看公告对话框 -->
    <el-dialog
      title="查看公告"
      v-model="viewDialogVisible"
      width="50%"
    >
      <div class="view-notice">
        <h3>{{ viewNotice.title }}</h3>
        <div class="notice-info">
          <span>发布人：{{ viewNotice.publisher_id }}</span>
          <span>发布时间：{{ formatDateTime(viewNotice.publish_time) }}</span>
          <span>状态：{{ viewNotice.status === 'published' ? '已发布' : '草稿' }}</span>
        </div>
        <div class="notice-content">
          {{ viewNotice.content }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { Plus, Edit, Delete, Search, Refresh, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 查询参数
const queryParams = ref({
  title: '',
  status: '',
  pageNum: 1,
  pageSize: 10
})

// 公告列表数据
const noticeList = ref([])
const total = ref(0)

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const viewDialogVisible = ref(false)
const viewNotice = ref({})
const noticeFormRef = ref()
const noticeForm = ref({
  title: '',
  content: '',
  status: 'published'
})

// 表单验证规则
const noticeRules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
  status: [{ required: true, message: '请选择公告状态', trigger: 'change' }]
}

// 导入API
import { noticeApi } from '../api/index.js'


const formatDateTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : ''
}
// 查询公告列表
const handleQuery = async () => {
  try {
    const res = await noticeApi.getNoticeList(queryParams.value)
    noticeList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取公告列表失败：', error)
    ElMessage.error('获取公告列表失败')
  }
}

// 重置查询条件
const resetQuery = () => {
  queryParams.value = {
    title: '',
    status: '',
    pageNum: 1,
    pageSize: 10
  }
  handleQuery()
}

// 重置表单
const resetForm = () => {
  noticeForm.value = {
    title: '',
    content: '',
    status: 'published'
  }
  noticeFormRef.value?.resetFields()
}

// 发布公告
const handlePublish = () => {
  dialogTitle.value = '发布公告'
  dialogVisible.value = true
  resetForm()
}

// 编辑公告
const handleEdit = (row) => {
  dialogTitle.value = '编辑公告'
  dialogVisible.value = true
  noticeForm.value = { ...row }
}

// 查看公告
const handleView = (row) => {
  viewNotice.value = row
  viewDialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!noticeFormRef.value) return
  await noticeFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (noticeForm.value.id) {
          // 更新公告
          await noticeApi.updateNotice(noticeForm.value.id, noticeForm.value)
          ElMessage.success('更新成功')
        } else {
          // 创建公告
          await noticeApi.createNotice(noticeForm.value)
          ElMessage.success('发布成功')
        }
        dialogVisible.value = false
        handleQuery()
      } catch (error) {
        console.error('操作失败：', error)
        ElMessage.error('操作失败')
      }
    }
  })
}

// 删除公告
const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除标题为"${row.title}"的公告吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await noticeApi.deleteNotice(row.id)
      ElMessage.success('删除成功')
      handleQuery()
    } catch (error) {
      console.error('删除公告失败：', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 分页大小改变
const handleSizeChange = (val) => {
  queryParams.value.pageSize = val
  handleQuery()
}

// 当前页改变
const handleCurrentChange = (val) => {
  queryParams.value.pageNum = val
  handleQuery()
}

onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
.notice-container {
  padding: 20px;
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.notice-content {
  background-color: #fff;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.view-notice {
  padding: 20px;
}

.view-notice h3 {
  margin-bottom: 15px;
  text-align: center;
}

.notice-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  color: #666;
}

.notice-content {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
}
</style>