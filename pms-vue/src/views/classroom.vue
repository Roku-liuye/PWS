<template>
  <div class="classroom-container">
    <div class="classroom-header">
      <h2>课室租借</h2>
      <el-button type="primary" @click="handleAdd" v-if = "userInfo.role === 'admin'">
        <el-icon><Plus /></el-icon>添加课室
      </el-button>
    </div>

    <el-card class="classroom-content">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="教室编号">
          <el-input v-model="queryParams.roomNo" placeholder="请输入教室编号" clearable />
        </el-form-item>
        <el-form-item label="教学楼">
          <el-select style="min-width: 160px" v-model="queryParams.building" placeholder="请选择教学楼" clearable>
            <el-option label="教学楼A" value="教学楼A" />
            <el-option label="教学楼B" value="教学楼B" />
            <el-option label="教学楼C" value="教学楼C" />
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
        <el-table-column prop="room_no" label="教室编号" width="120" />
        <el-table-column prop="building" label="教学楼" width="120" />
        <el-table-column prop="type" label="教室类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'multimedia' ? 'success' : 'info'">
              {{ scope.row.type === 'multimedia' ? '多媒体教室' : '普通教室' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容纳人数" width="120" />
        <el-table-column prop="facilities" label="设施配置" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.facilities || '暂无配置信息' }}
          </template>
        </el-table-column>
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

    <!-- 添加课室对话框 -->
    <el-dialog
      v-model="addFormVisible"
      title="添加课室"
      width="500px"
      append-to-body
    >
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="100px">
        <el-form-item label="教室编号" prop="roomNo">
          <el-input v-model="addForm.roomNo" placeholder="请输入教室编号" />
        </el-form-item>
        <el-form-item label="教学楼" prop="building">
          <el-select v-model="addForm.building" placeholder="请选择教学楼">
            <el-option label="教学楼A" value="教学楼A" />
            <el-option label="教学楼B" value="教学楼B" />
            <el-option label="教学楼C" value="教学楼C" />
          </el-select>
        </el-form-item>
        <el-form-item label="教室类型" prop="type">
          <el-select v-model="addForm.type" placeholder="请选择教室类型">
            <el-option label="多媒体教室" value="multimedia" />
            <el-option label="普通教室" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="容纳人数" prop="capacity">
          <el-input-number v-model="addForm.capacity" :min="1" />
        </el-form-item>
        <el-form-item label="设施配置" prop="facilities">
          <el-input
            v-model="addForm.facilities"
            type="textarea"
            placeholder="请输入设施配置信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitAdd">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="教室详情"
      width="500px"
      append-to-body
    >
      <div class="classroom-detail" v-if="currentClassroom">
        <div class="detail-item">
          <span class="label">教室编号：</span>
          <span class="value">{{ currentClassroom.room_no }}</span>
        </div>
        <div class="detail-item">
          <span class="label">教学楼：</span>
          <span class="value">{{ currentClassroom.building }}</span>
        </div>
        <div class="detail-item">
          <span class="label">教室类型：</span>
          <span class="value">
            <el-tag :type="currentClassroom.type === 'multimedia' ? 'success' : 'info'">
              {{ currentClassroom.type === 'multimedia' ? '多媒体教室' : '普通教室' }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="label">容纳人数：</span>
          <span class="value">{{ currentClassroom.capacity }} 人</span>
        </div>
        <div class="detail-item">
          <span class="label">设施配置：</span>
          <span class="value">{{ currentClassroom.facilities || '暂无配置信息' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">使用状态：</span>
          <span class="value">
            <el-tag :type="currentClassroom.status === 'available' ? 'success' : 'danger'">
              {{ currentClassroom.status === 'available' ? '空闲' : '已预约' }}
            </el-tag>
          </span>
        </div>
      </div>
    </el-dialog>

    <!-- 预约表单对话框 -->
    <el-dialog
      v-model="bookingFormVisible"
      title="预约课室"
      width="500px"
      append-to-body
    >
      <el-form ref="bookingFormRef" :model="bookingForm" :rules="bookingRules" label-width="100px">
        <el-form-item label="教室编号" prop="classroom_id">
          <el-input v-model="bookingForm.classroom_id" disabled />
        </el-form-item>
        <el-form-item label="预约日期" prop="booking_date">
          <el-date-picker
            v-model="bookingForm.booking_date"
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
import { ElMessage } from 'element-plus'
import { classroomApi, userApi } from '../api/index.js'


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

// 查询参数
const queryParams = ref({
  roomNo: '',
  building: '',
  date: '',
  page: 1,
  page_size: 10
})

// 教室列表数据
const classroomList = ref([])
const total = ref(0)

// 获取教室列表数据
const getList = async () => {
  try {
    const res = await classroomApi.getClassroomList(queryParams.value)
    classroomList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取教室列表失败：', error)
    ElMessage.error('获取教室列表失败')
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
    roomNo: '',
    building: '',
    date: '',
    page: 1,
    page_size: 10
  }
  getList()
}

// 详情相关
const detailDialogVisible = ref(false)
const currentClassroom = ref(null)

// 查看详情
const handleDetail = async (row) => {
  try {
    const res = await classroomApi.getClassroomDetail(row.id)
    currentClassroom.value = res
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取详情失败：', error)
    ElMessage.error('获取详情失败')
  }
}

// 添加课室相关
const addFormVisible = ref(false)
const addFormRef = ref()
const addForm = ref({
  roomNo: '',
  building: '',
  type: '',
  capacity: 0,
  facilities: ''
})

const addRules = {
  roomNo: [{ required: true, message: '请输入教室编号', trigger: 'blur' }],
  building: [{ required: true, message: '请选择教学楼', trigger: 'change' }],
  type: [{ required: true, message: '请选择教室类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入容纳人数', trigger: 'blur' }]
}

// 打开添加表单
const handleAdd = () => {
  addForm.value = {
    roomNo: '',
    building: '',
    type: '',
    capacity: 0,
    facilities: ''
  }
  addFormVisible.value = true
}

// 提交添加
const submitAdd = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 转换字段名
        const submitData = {
          room_no: addForm.value.roomNo,
          building: addForm.value.building,
          type: addForm.value.type,
          capacity: addForm.value.capacity,
          facilities: addForm.value.facilities
        }
        await classroomApi.createClassroom(submitData)
        ElMessage.success('添加成功')
        addFormVisible.value = false
        getList()
      } catch (error) {
        console.error('添加失败：', error)
        const errorMessage = error.response?.data?.detail || error.message || '添加失败'
        ElMessage.error(errorMessage)
      }
    }
  })
}

// 预约相关
const bookingFormVisible = ref(false)
const bookingFormRef = ref()
const bookingForm = ref({
  classroom_id: '',
  booking_date: '',
  timeSlot: '',
  purpose: '',
  start_time: '',
  end_time: ''
})

const bookingRules = {
  booking_date: [{ required: true, message: '请选择预约日期', trigger: 'change' }],
  timeSlot: [{ required: true, message: '请选择时间段', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入用途说明', trigger: 'blur' }]
}

// 禁用过去的日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 打开预约表单
const handleBooking = (row) => {
  bookingForm.value = {
    classroom_id: row.id,
    user_id: row.user_id,
    booking_date: row.booking_date,
    start_time: '',
    end_time: '',
    purpose: '',
    status: 'pending'
  }
  bookingFormVisible.value = true
}

// 提交预约
const submitBooking = async () => {
  if (!bookingFormRef.value) return
  await bookingFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const timeSlot = getTimeBySlot(bookingForm.value.timeSlot)
        await classroomApi.submitBooking({
          classroom_id: bookingForm.value.classroom_id,
          purpose: bookingForm.value.purpose,
          booking_date: bookingForm.value.booking_date,
          start_time: timeSlot.start,
          end_time: timeSlot.end
        })
        ElMessage.success('预约成功')
        bookingFormVisible.value = false
        getList()
      } catch (error) {
        console.error('预约失败：', error)
        const errorMessage = error.response?.data?.detail || error.message || '预约失败'
        ElMessage.error(errorMessage)
      }
    }
  })
}

// 根据时间段获取具体时间
const getTimeBySlot = (slot) => {
  const timeMap = {
    morning: { start: '08:00', end: '12:00' },
    afternoon: { start: '14:00', end: '18:00' },
    evening: { start: '19:00', end: '22:00' }
  }
  return timeMap[slot] || { start: '', end: '' }
}

// 分页相关
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
  getUserInfo()
})
</script>

<style scoped>
.classroom-container {
  padding: 20px;
}

.classroom-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.classroom-detail {
  padding: 20px;
}

.detail-item {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.detail-item .label {
  width: 100px;
  color: #606266;
}

.detail-item .value {
  flex: 1;
  color: #303133;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>