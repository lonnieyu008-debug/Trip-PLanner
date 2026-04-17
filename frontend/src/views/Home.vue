<template>
  <div class="home-container">

    <!-- ===== 左侧：品牌/视觉区 ===== -->
    <div class="left-panel">
      <div class="left-inner">
        <!-- Logo 区 -->
        <div class="brand">
          <span class="brand-icon">🧭</span>
          <span class="brand-name">旅行规划助手</span>
        </div>

        <!-- 主标语 -->
        <h1 class="hero-title">
          下一站<br/>
          <span class="hero-highlight">去哪里？</span>
        </h1>
        <p class="hero-sub">告诉 AI 你的目的地和偏好，<br/>几分钟内获得一份专属行程</p>

        <!-- 特性列表 -->
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>实时搜索景点 · 天气 · 酒店</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>多 Agent 并行规划，快速生成</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>支持编辑、导出图片和 PDF</span>
          </div>
        </div>

        <!-- 地图装饰 SVG -->
        <div class="deco-map">
          <svg viewBox="0 0 400 260" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 地图轮廓装饰 -->
            <path d="M30 200 Q80 140 140 160 Q200 180 240 120 Q280 60 350 80" stroke="rgba(255,255,255,0.25)" stroke-width="2.5" stroke-dasharray="6 4" fill="none"/>
            <!-- 路径点 -->
            <circle cx="30" cy="200" r="7" fill="rgba(255,255,255,0.5)"/>
            <circle cx="140" cy="160" r="7" fill="rgba(255,255,255,0.5)"/>
            <circle cx="240" cy="120" r="7" fill="rgba(255,255,255,0.5)"/>
            <circle cx="350" cy="80" r="9" fill="#ffd580"/>
            <!-- 终点 Pin -->
            <path d="M350 80 Q350 50 330 40 Q310 30 310 55 Q310 70 350 80Z" fill="#ffd580" opacity="0.9"/>
            <circle cx="330" cy="52" r="5" fill="#3d1f0a"/>
            <!-- 飞机图标 -->
            <text x="170" y="100" font-size="28" fill="rgba(255,255,255,0.6)" transform="rotate(-25 170 100)">✈</text>
            <!-- 装饰圆圈 -->
            <circle cx="80" cy="60" r="30" stroke="rgba(255,255,255,0.12)" stroke-width="1.5" fill="none"/>
            <circle cx="80" cy="60" r="18" stroke="rgba(255,255,255,0.08)" stroke-width="1" fill="none"/>
            <circle cx="310" cy="200" r="40" stroke="rgba(255,255,255,0.1)" stroke-width="1.5" fill="none"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- ===== 右侧：表单区 ===== -->
    <div class="right-panel">
      <div class="form-wrapper">
        <div class="form-header">
          <h2 class="form-title">规划我的行程</h2>
          <p class="form-subtitle">填写以下信息，AI 为你生成专属旅行方案</p>
        </div>

        <a-form :model="formData" layout="vertical" @finish="handleSubmit" class="trip-form">

          <!-- 目的地 -->
          <div class="field-group">
            <div class="field-label">🏙️ 目的地城市</div>
            <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地' }]">
              <a-input
                v-model:value="formData.city"
                placeholder="例如：成都、西安、厦门..."
                size="large"
                class="warm-input"
              />
            </a-form-item>
          </div>

          <!-- 日期行 -->
          <div class="field-row">
            <div class="field-group flex-1">
              <div class="field-label">📅 出发日期</div>
              <a-form-item name="start_date" :rules="[{ required: true, message: '请选择' }]">
                <a-date-picker
                  v-model:value="formData.start_date"
                  style="width: 100%"
                  size="large"
                  placeholder="开始日期"
                  class="warm-input"
                />
              </a-form-item>
            </div>
            <div class="date-arrow">→</div>
            <div class="field-group flex-1">
              <div class="field-label">📅 返回日期</div>
              <a-form-item name="end_date" :rules="[{ required: true, message: '请选择' }]">
                <a-date-picker
                  v-model:value="formData.end_date"
                  style="width: 100%"
                  size="large"
                  placeholder="结束日期"
                  class="warm-input"
                />
              </a-form-item>
            </div>
            <div class="days-chip" v-if="formData.travel_days > 0">
              {{ formData.travel_days }}<span style="font-size:11px;font-weight:400;">天</span>
            </div>
          </div>

          <!-- 交通 + 住宿 -->
          <div class="field-row">
            <div class="field-group flex-1">
              <div class="field-label">🚗 交通方式</div>
              <a-form-item name="transportation">
                <a-select v-model:value="formData.transportation" size="large" class="warm-input">
                  <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                  <a-select-option value="自驾">🚗 自驾</a-select-option>
                  <a-select-option value="步行">🚶 步行</a-select-option>
                  <a-select-option value="混合">🔀 混合</a-select-option>
                </a-select>
              </a-form-item>
            </div>
            <div class="field-group flex-1">
              <div class="field-label">🏨 住宿偏好</div>
              <a-form-item name="accommodation">
                <a-select v-model:value="formData.accommodation" size="large" class="warm-input">
                  <a-select-option value="经济型酒店">💰 经济型酒店</a-select-option>
                  <a-select-option value="舒适型酒店">🏨 舒适型酒店</a-select-option>
                  <a-select-option value="豪华酒店">⭐ 豪华酒店</a-select-option>
                  <a-select-option value="民宿">🏡 民宿</a-select-option>
                </a-select>
              </a-form-item>
            </div>
          </div>

          <!-- 旅行偏好 -->
          <div class="field-group">
            <div class="field-label">🎯 旅行偏好 <span class="field-label-hint">（可多选）</span></div>
            <a-form-item name="preferences">
              <div class="pref-grid">
                <label
                  v-for="pref in preferenceOptions"
                  :key="pref.value"
                  class="pref-chip"
                  :class="{ selected: formData.preferences.includes(pref.value) }"
                  @click="togglePreference(pref.value)"
                >
                  <span>{{ pref.icon }}</span>
                  <span>{{ pref.label }}</span>
                </label>
              </div>
            </a-form-item>
          </div>

          <!-- 额外要求 -->
          <div class="field-group">
            <div class="field-label">💬 特别说明 <span class="field-label-hint">（选填）</span></div>
            <a-form-item name="free_text_input">
              <a-textarea
                v-model:value="formData.free_text_input"
                placeholder="有什么特别想去的地方？有没有忌口或特殊需求？尽管告诉我..."
                :rows="3"
                size="large"
                class="warm-input"
              />
            </a-form-item>
          </div>

          <!-- 进度条（加载时显示） -->
          <div v-if="loading" class="progress-block">
            <a-progress
              :percent="loadingProgress"
              status="active"
              :stroke-color="{ '0%': '#e8651a', '100%': '#c04e0e' }"
              :stroke-width="8"
              :show-info="false"
            />
            <p class="progress-status">{{ loadingStatus }}</p>
          </div>

          <!-- 提交按钮 -->
          <a-form-item>
            <button type="submit" class="submit-btn" :class="{ loading: loading }" :disabled="loading">
              <span v-if="!loading">✈️ &nbsp; 开始规划</span>
              <span v-else>⏳ &nbsp; {{ loadingStatus }}</span>
            </button>
          </a-form-item>

        </a-form>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

// 本地表单状态类型（日期用 Dayjs 对象，提交时转换为字符串）

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')

const preferenceOptions = [
  { value: '历史文化', label: '历史文化', icon: '🏛️' },
  { value: '自然风光', label: '自然风光', icon: '🏞️' },
  { value: '美食',   label: '美食',   icon: '🍜' },
  { value: '购物',   label: '购物',   icon: '🛍️' },
  { value: '艺术',   label: '艺术',   icon: '🎨' },
  { value: '休闲',   label: '休闲',   icon: '☕' },
]

interface FormState {
  city: string
  start_date: Dayjs | null
  end_date: Dayjs | null
  travel_days: number
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}

const formData = reactive<FormState>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const togglePreference = (val: string) => {
  const idx = formData.preferences.indexOf(val)
  if (idx === -1) formData.preferences.push(val)
  else formData.preferences.splice(idx, 1)
}

watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      formData.end_date = null
    } else {
      message.warning('结束日期不能早于开始日期')
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在初始化...'

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10
      if (loadingProgress.value <= 30)      loadingStatus.value = '🔍 正在搜索景点...'
      else if (loadingProgress.value <= 50) loadingStatus.value = '🌤️ 正在查询天气...'
      else if (loadingProgress.value <= 70) loadingStatus.value = '🏨 正在推荐酒店...'
      else                                  loadingStatus.value = '📋 正在生成行程计划...'
    }
  }, 500)

  try {
    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input
    }

    const response = await generateTripPlan(requestData)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingStatus.value = '✅ 完成！'

    if (response.success && response.data) {
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      sessionStorage.setItem('tripRequest', JSON.stringify(requestData))  // 存原始请求，供编辑时复用
      message.success('旅行计划生成成功！')
      setTimeout(() => router.push('/result'), 500)
    } else {
      message.error(response.message || '生成失败')
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    message.error(error.message || '生成失败，请稍后重试')
  } finally {
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
    }, 1000)
  }
}
</script>

<style scoped>
/* ===== 整体：左右等高分栏 ===== */
.home-container {
  display: flex;
  min-height: calc(100vh - 64px - 52px); /* 减去 header 和 footer */
}

/* ===== 左侧面板 ===== */
.left-panel {
  width: 42%;
  flex-shrink: 0;
  background: linear-gradient(160deg, #3d1f0a 0%, #7a4a28 55%, #b06030 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 60px 48px;
}

.left-inner {
  position: relative;
  z-index: 2;
  width: 100%;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 48px;
}

.brand-icon {
  font-size: 22px;
}

.brand-name {
  font-size: 15px;
  color: rgba(255,255,255,0.7);
  letter-spacing: 2px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  color: white;
  line-height: 1.15;
  margin: 0 0 20px;
  letter-spacing: 2px;
}

.hero-highlight {
  color: #ffd580;
}

.hero-sub {
  font-size: 15px;
  color: rgba(255,255,255,0.7);
  line-height: 1.8;
  margin: 0 0 40px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255,255,255,0.8);
}

.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffd580;
  flex-shrink: 0;
}

.deco-map {
  width: 100%;
  opacity: 0.9;
}

/* ===== 右侧面板 ===== */
.right-panel {
  flex: 1;
  background: #faf6f1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  overflow-y: auto;
}

.form-wrapper {
  width: 100%;
  max-width: 520px;
}

.form-header {
  margin-bottom: 28px;
}

.form-title {
  font-size: 28px;
  font-weight: 800;
  color: #3d1f0a;
  margin: 0 0 6px;
}

.form-subtitle {
  font-size: 14px;
  color: #a0784a;
  margin: 0;
}

/* ===== 字段通用 ===== */
.field-group {
  margin-bottom: 4px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #7a4a28;
  margin-bottom: 6px;
}

.field-label-hint {
  font-weight: 400;
  color: #c4a070;
}

/* 横排两列 */
.field-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 4px;
}

.flex-1 {
  flex: 1;
  min-width: 0;
}

.date-arrow {
  font-size: 18px;
  color: #c4a070;
  padding-bottom: 28px;
  flex-shrink: 0;
}

.days-chip {
  background: #e8651a;
  color: white;
  border-radius: 10px;
  padding: 4px 12px;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  flex-shrink: 0;
  line-height: 1.4;
  margin-bottom: 28px;
}

/* ===== 输入框统一暖色风格 ===== */
.warm-input :deep(.ant-input),
.warm-input :deep(.ant-picker),
.warm-input :deep(.ant-select-selector),
.warm-input :deep(.ant-input-affix-wrapper) {
  border-radius: 10px !important;
  border: 1.5px solid #e8d5bc !important;
  background: #fffcf8 !important;
  color: #3d1f0a;
  transition: all 0.2s;
}

.warm-input :deep(.ant-input:focus),
.warm-input :deep(.ant-picker-focused),
.warm-input :deep(.ant-select-focused .ant-select-selector) {
  border-color: #e8651a !important;
  box-shadow: 0 0 0 3px rgba(232,101,26,0.1) !important;
}

.warm-input :deep(.ant-input:hover),
.warm-input :deep(.ant-picker:hover),
.warm-input :deep(.ant-select-selector:hover) {
  border-color: #e8651a !important;
}

/* ===== 偏好标签网格 ===== */
.pref-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pref-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  border-radius: 20px;
  border: 1.5px solid #e8d5bc;
  background: white;
  font-size: 13px;
  color: #7a4a28;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.pref-chip:hover {
  border-color: #e8651a;
  background: #fff5ee;
}

.pref-chip.selected {
  border-color: #e8651a;
  background: #e8651a;
  color: white;
}

/* ===== 进度条 ===== */
.progress-block {
  background: #fffaf5;
  border: 1.5px dashed #e8651a;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 12px;
}

.progress-status {
  margin: 10px 0 0;
  color: #e8651a;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

/* ===== 提交按钮（原生 button，彻底自定义） ===== */
.submit-btn {
  width: 100%;
  height: 52px;
  border-radius: 26px;
  border: none;
  background: linear-gradient(135deg, #e8651a 0%, #c04e0e 100%);
  color: white;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(232,101,26,0.35);
  transition: all 0.25s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(232,101,26,0.45);
  background: linear-gradient(135deg, #f07530 0%, #d05a18 100%);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled,
.submit-btn.loading {
  opacity: 0.75;
  cursor: not-allowed;
  transform: none;
}

/* 响应式：小屏幕变上下布局 */
@media (max-width: 900px) {
  .home-container { flex-direction: column; }
  .left-panel { width: 100%; min-height: 280px; padding: 40px 32px; }
  .hero-title { font-size: 40px; }
  .right-panel { padding: 32px 24px; }
  .deco-map { display: none; }
}
</style>
