<template>
  <div class="test-edge-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试Edge页面</span>
        </div>
      </template>
      <div class="test-content">
        <el-alert
          title="操作说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>1. 确保Edge浏览器已打开并显示要测试的页面</p>
          <p>2. 点击下方按钮开始测试</p>
          <p>3. 系统将自动抓取页面、分析内容并执行测试</p>
        </el-alert>
        
        <el-form :model="form" label-width="120px" class="test-form">
          <el-form-item label="测试页面URL">
            <el-input v-model="form.pageUrl" placeholder="请输入测试页面的URL，例如 https://letcode.in/test" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="startTest" :loading="isTesting">
              开始测试Edge页面
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="testResult" class="test-result">
          <el-card class="result-card">
            <template #header>
              <span>测试结果</span>
            </template>
            <el-descriptions :column="1">
              <el-descriptions-item label="测试状态">{{ testResult.success ? '成功' : '失败' }}</el-descriptions-item>
              <el-descriptions-item label="测试消息">{{ testResult.message }}</el-descriptions-item>
              <el-descriptions-item label="测试页面">{{ testResult.page_info ? testResult.page_info.title || '未知页面' : '未知页面' }}</el-descriptions-item>
              <el-descriptions-item label="页面URL">{{ testResult.page_info ? testResult.page_info.url || '未输入' : '未输入' }}</el-descriptions-item>
              <el-descriptions-item label="识别到的文本数量">{{ testResult.ocr_results ? testResult.ocr_results.length : 0 }}</el-descriptions-item>
              <el-descriptions-item label="执行的测试步骤">{{ testResult.test_steps ? testResult.test_steps.length : 0 }}</el-descriptions-item>
            </el-descriptions>
            
            <!-- 截图显示区域 -->
            <el-card v-if="testResult.page_info && testResult.page_info.screenshot_taken" class="screenshot-card">
              <template #header>
                <span>测试页面截图</span>
              </template>
              <div class="screenshot-container">
                <img :src="getScreenshotUrl()" alt="测试页面截图" class="screenshot-image" />
                <div class="screenshot-info">
                  <p>截图文件名: {{ testResult.page_info.screenshot_path }}</p>
                  <p>截图时间: {{ testResult.page_info.timestamp }}</p>
                </div>
              </div>
            </el-card>
            
            <!-- 所有页面截图 -->
            <el-card v-if="testResult.all_screenshots && testResult.all_screenshots.length > 0" class="screenshot-card">
              <template #header>
                <span>所有页面截图</span>
              </template>
              <div class="all-screenshots">
                <div v-for="(screenshot, index) in testResult.all_screenshots" :key="index" class="screenshot-item">
                  <img :src="`http://localhost:8000/api/screenshots/${screenshot.filename}`" alt="页面截图" class="screenshot-thumbnail" />
                  <div class="screenshot-item-info">
                    <p>截图文件名: {{ screenshot.filename }}</p>
                    <p>截图时间: {{ screenshot.timestamp }}</p>
                  </div>
                </div>
              </div>
            </el-card>
            
            <!-- 测试记忆 -->
            <el-card v-if="testResult.test_memory" class="memory-card">
              <template #header>
                <span>测试记忆</span>
              </template>
              <div class="memory-info">
                <el-collapse>
                  <el-collapse-item title="访问过的页面">
                    <el-list>
                      <el-list-item v-for="(page, index) in testResult.test_memory.visited_pages" :key="index">
                        <div>
                          <span class="page-title">{{ page.title }}</span>
                          <span class="page-url">{{ page.url }}</span>
                          <span class="page-time">{{ page.timestamp }}</span>
                        </div>
                      </el-list-item>
                    </el-list>
                  </el-collapse-item>
                  <el-collapse-item title="完成的测试步骤">
                    <el-list>
                      <el-list-item v-for="(step, index) in testResult.test_memory.completed_steps" :key="index">
                        <div>
                          <span class="step-action">{{ step.action }}</span>
                          <span v-if="step.text"> - {{ step.text }}</span>
                        </div>
                      </el-list-item>
                    </el-list>
                  </el-collapse-item>
                  <el-collapse-item title="测试历史">
                    <el-list>
                      <el-list-item v-for="(history, index) in testResult.test_memory.test_history" :key="index">
                        <div>
                          <span class="history-time">{{ history.timestamp }}</span>
                          <span class="history-page">{{ history.page_info.title }}</span>
                        </div>
                      </el-list-item>
                    </el-list>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
            
            <el-divider />
            
            <el-card v-if="testResult.ocr_results && testResult.ocr_results.length > 0">
              <template #header>
                <span>识别到的文本</span>
              </template>
              <el-scrollbar height="200px">
                <el-table :data="testResult.ocr_results" style="width: 100%">
                  <el-table-column prop="text" label="文本" />
                  <el-table-column prop="position" label="位置" width="200">
                    <template #default="scope">
                      {{ `(${scope.row.position[0]}, ${scope.row.position[1]})` }}
                    </template>
                  </el-table-column>
                </el-table>
              </el-scrollbar>
            </el-card>
            
            <el-card v-if="testResult.test_steps && testResult.test_steps.length > 0">
              <template #header>
                <span>执行的测试步骤</span>
              </template>
              <el-list>
                <el-list-item v-for="(step, index) in testResult.test_steps" :key="index">
                  <template #default>
                    <div>
                      <span class="step-action">{{ step.action }}</span>
                      <span v-if="step.text"> - 目标: {{ step.text }}</span>
                      <span v-if="step.x && step.y"> - 坐标: ({{ step.x }}, {{ step.y }})</span>
                    </div>
                  </template>
                </el-list-item>
              </el-list>
            </el-card>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const isTesting = ref(false)
const testResult = ref(null)
const form = reactive({
  pageUrl: ''
})

const startTest = async () => {
  try {
    isTesting.value = true
    testResult.value = null
    
    const response = await axios.post('http://localhost:8000/api/test/edge', {
      page_url: form.pageUrl
    })
    testResult.value = response.data
  } catch (error) {
    console.error('测试Edge页面失败:', error)
    testResult.value = {
      success: false,
      message: '测试失败: ' + (error.response?.data?.detail || error.message)
    }
  } finally {
    isTesting.value = false
  }
}

const getScreenshotUrl = () => {
  if (testResult.value && testResult.value.page_info && testResult.value.page_info.screenshot_path) {
    return `http://localhost:8000/api/screenshots/${testResult.value.page_info.screenshot_path}`
  }
  return ''
}
</script>

<style scoped>
.test-edge-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-content {
  margin-top: 20px;
}

.test-actions {
  margin: 20px 0;
  text-align: center;
}

.test-result {
  margin-top: 30px;
}

.result-card {
  margin-top: 20px;
}

.step-action {
  font-weight: bold;
  margin-right: 10px;
}

.screenshot-card {
  margin-top: 20px;
}

.screenshot-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.screenshot-image {
  max-width: 100%;
  max-height: 500px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.screenshot-info {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.all-screenshots {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.screenshot-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  width: 200px;
}

.screenshot-thumbnail {
  width: 180px;
  height: 120px;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.screenshot-item-info {
  text-align: center;
  font-size: 12px;
  color: #666;
}

.memory-card {
  margin-top: 20px;
}

.memory-info {
  font-size: 14px;
}

.page-title {
  font-weight: bold;
  margin-right: 10px;
}

.page-url {
  color: #409eff;
  margin-right: 10px;
}

.page-time {
  color: #999;
  font-size: 12px;
}

.history-time {
  color: #999;
  font-size: 12px;
  margin-right: 10px;
}

.history-page {
  font-weight: bold;
}
</style>