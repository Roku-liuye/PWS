<template>
  <div class="classroom-container">
    <div class="classroom-header">
      <h2>课室租借</h2>
      <el-button type="primary" @click="handleBooking">
        <el-icon><Plus /></el-icon>预约课室
      </el-button>
    </div>

    <el-card class="classroom-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="教室编号">
          <el-input v-model="queryParams.roomNo" placeholder="请输入教室编号" clearable />
        </el-form-item>
        <el-form-item label="教学楼">
          <el-select v-model="queryParams.building" placeholder="请选择教学楼" clearable>
            <el-option label="A教学楼" value="A" />
            <el-option label="B教学楼" value="B" />
            <el-option label="C教学楼" value="C" />
          </el-select>
        </el-form-item>
        <el-form-item label="预约日期">
          <el-date-picker
            v-model="queryParams.date"
            type="date"
            placeholder="选择日期"
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

      <el-table :data="classroomList" border style="width: 100%">
        <el-table-column prop="roomNo" label="教室编号" width="120" />
        <el-table-column prop="building" label="教学楼" width="120" />
        <el-table-column prop="type" label="教室类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'multimedia' ? 'success' : 'info'">
              {{ scope.row.type === 'multimedia' ? '多媒体教室' : '普通教室' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容纳人数" width="120" />
        <el-table-column prop="facilities" label="设施配置" show-overflow-tooltip />
        <el-table-column prop="status" label="使用状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'available' ? 'success' : 'danger'">
              {{ scope.row.status === 'available' ? '空闲' : '已预约' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" link @click="handleDetail(scope.row)">
                <el-icon><View /></el-icon>详情
              </el-button>
              <el-button
                type="success"
                link
                @click="handleBooking(scope.row)"
                v-if="scope.row.status === 'available'"
              >
                <el-icon><Calendar /></el-icon>预约
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

    <!-- 预约表单对话框 -->
    <el-dialog
      v-model="bookingFormVisible"
      title="预约课室"
      width="500px"
      append-to-body
    >
      <el-form ref="bookingFormRef" :model="bookingForm" :rules="bookingRules" label-width="100px">
        <el-form-item label="教室编号" prop="roomNo">
          <el-input v-model="bookingForm.roomNo" disabled />
        </el-form-item>
        <el-form-item label="预约日期" prop="date">
          <el-date-picker
            v-model="bookingForm.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="时间段" prop="timeSlot">
          <el-select v-model="bookingForm.timeSlot" placeholder="请选择时间段">
            <el-option label="上午 08:00-12:00" value="morning" />
            <el-option label="下午 14:00-18:00" value="afternoon" />
            <el-option label="晚上 19:00-22:00" value="evening" />
          </el-select>
        </el-form-item>
        <el-form-item label="用途说明" prop="purpose">
          <el-input
            v-model="bookingForm.purpose"
            type="textarea"
            placeholder="请简要说明用途"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="bookingFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitBooking">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search, Refresh, View, Calendar } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 查询参数
const queryParams = ref({
  roomNo: '',
  building: '',
  date: '',
  pageNum: 1,
  pageSize: 10
})

// 教室列表数据
const classroomList = ref([])
const total = ref(0)

// 获取教室列表数据
const getList = async () => {
  try {
    // TODO: 调用后端API获取数据
    // const { data } = await getClassroomList(queryParams.value)
    // classroomList.value = data.list
    // total.value = data.total

    // 模拟数据
    classroomList.value = [
      {
        roomNo: 'A101',
        building: 'A教学楼',
        type: 'multimedia',
        capacity: 120,
        facilities: '多媒体设备、空调、投影仪',
        status: 'available'
      }
    ]
    total.value = 1
  } catch (error) {
    console.error('获取教室列表失败：', error)
    ElMessage.error('获取教室列表失败')
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
    roomNo: '',
    building: '',
    date: '',
    pageNum: 1,
    pageSize: 10
  }
  getList()
}

// 查看详情
const handleDetail = (row) => {
  ElMessage('查看教室详情：' + row.roomNo)
}

// 预约相关
const bookingFormVisible = ref(false)
const bookingFormRef = ref()
const bookingForm = ref({
  roomNo: '',
  date: '',
  timeSlot: '',
  purpose: ''
})

const bookingRules = {
  date: [{ required: true, message: '请选择预约日期', trigger: 'change' }],
  timeSlot: [{ required: true, message: '请选择时间段', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入用途说明', trigger: 'blur' }]
}

// 禁用日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 不能选择过去的日期
}

// 打开预约表单
const handleBooking = (row) => {
  bookingForm.value = {
    roomNo: row ? row.roomNo : '',
    date: '',
    timeSlot: '',
    purpose: ''
  }
  bookingFormVisible.value = true
}

// 提交预约
const submitBooking = async () => {
  if (!bookingFormRef.value) return
  await bookingFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: 调用后端API提交预约
        // await submitBookingForm(bookingForm.value)
        ElMessage.success('预约成功')
        bookingFormVisible.value = false
        getList()
      } catch (error) {
        console.error('提交预约失败：', error)
        ElMessage.error('预约失败')
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
.classroom-container {
  padding: 20px;
}

.classroom-header {
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