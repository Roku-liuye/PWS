<template>
  <div class="repair-submit-container">
    <el-card class="repair-form-card">
      <template #header>
        <div class="card-header">
          <h2>提交报修</h2>
        </div>
      </template>
      
      <el-form
        ref="repairFormRef"
        :model="repairForm"
        :rules="repairRules"
        label-width="100px"
        class="repair-form">
        
        <el-form-item label="报修类型" prop="type">
          <el-select v-model="repairForm.type" placeholder="请选择报修类型">
            <el-option label="设备报修" value="equipment" />
            <el-option label="设施报修" value="facility" />
          </el-select>
        </el-form-item>

        <el-form-item label="资产编号" prop="asset_id">
          <el-input v-model="repairForm.asset_id" placeholder="请输入资产编号（选填）" />
        </el-form-item>

        <el-form-item label="报修位置" prop="location">
          <el-input v-model="repairForm.location" placeholder="请输入报修位置" />
        </el-form-item>

        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="repairForm.description"
            type="textarea"
            rows="4"
            placeholder="请详细描述问题"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitRepair" :loading="loading">
            提交报修
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { repairApi } from '../api'

const repairFormRef = ref(null)
const loading = ref(false)

const repairForm = reactive({
  type: '',
  asset_id: '',
  location: '',
  description: ''
})

const repairRules = {
  type: [{ required: true, message: '请选择报修类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入报修位置', trigger: 'blur' }],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }]
}

const submitRepair = async () => {
  if (!repairFormRef.value) return

  await repairFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        await repairApi.createRepair(repairForm)
        ElMessage.success('报修提交成功')
        // 重置表单
        repairFormRef.value.resetFields()
      } catch (error) {
        console.error('提交报修失败:', error)
        ElMessage.error('提交报修失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.repair-submit-container {
  padding: 20px;
}

.repair-form-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.repair-form {
  margin-top: 20px;
}
</style>