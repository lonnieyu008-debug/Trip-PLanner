<template>
  <div class="result-container">

    <!-- ===== 顶部英雄区 ===== -->
    <div v-if="tripPlan" class="hero-banner">
      <div class="hero-content">
        <div class="hero-left">
          <div class="hero-tag">✈️ AI 行程规划</div>
          <h1 class="hero-city">{{ tripPlan.city }}</h1>
          <p class="hero-dates">{{ tripPlan.start_date }} → {{ tripPlan.end_date }} · {{ tripPlan.days.length }}天{{ tripPlan.days.length }}夜</p>
          <p class="hero-suggestion">{{ tripPlan.overall_suggestions }}</p>
        </div>
        <div class="hero-right">
          <a-space size="small" wrap>
            <a-button class="btn-back" @click="goBack">← 重新规划</a-button>
            <a-button v-if="!editMode" class="btn-edit" @click="toggleEditMode">✏️ 编辑行程</a-button>
            <a-button v-else class="btn-save" type="primary" @click="saveChanges">💾 保存</a-button>
            <a-button v-if="editMode" class="btn-cancel" @click="cancelEdit">✕ 取消</a-button>
            <a-dropdown v-if="!editMode">
              <template #overlay>
                <a-menu>
                  <a-menu-item key="image" @click="exportAsImage">📷 导出图片</a-menu-item>
                  <a-menu-item key="pdf" @click="exportAsPDF">📄 导出 PDF</a-menu-item>
                </a-menu>
              </template>
              <a-button class="btn-export">📥 导出 <DownOutlined /></a-button>
            </a-dropdown>
          </a-space>
        </div>
      </div>

      <!-- AI 修改输入框（仅编辑模式显示） -->
      <div v-if="editMode" class="ai-edit-bar">
        <span class="ai-edit-icon">✨</span>
        <a-input
          v-model:value="aiInstruction"
          class="ai-edit-input"
          placeholder="用 AI 修改行程，例如：把第二天改轻松一点，减少景点数量"
          :disabled="aiLoading"
          @pressEnter="applyAiEdit"
        />
        <a-button
          class="ai-edit-btn"
          type="primary"
          :loading="aiLoading"
          @click="applyAiEdit"
        >
          {{ aiLoading ? 'AI 修改中...' : '发送' }}
        </a-button>
      </div>

      <!-- 预算条 -->
      <div v-if="tripPlan.budget" class="budget-bar">
        <div class="budget-bar-item">
          <span class="budget-bar-icon">🎡</span>
          <span class="budget-bar-label">景点门票</span>
          <span class="budget-bar-value">¥{{ tripPlan.budget.total_attractions }}</span>
        </div>
        <div class="budget-bar-divider"></div>
        <div class="budget-bar-item">
          <span class="budget-bar-icon">🏨</span>
          <span class="budget-bar-label">酒店住宿</span>
          <span class="budget-bar-value">¥{{ tripPlan.budget.total_hotels }}</span>
        </div>
        <div class="budget-bar-divider"></div>
        <div class="budget-bar-item">
          <span class="budget-bar-icon">🍜</span>
          <span class="budget-bar-label">餐饮费用</span>
          <span class="budget-bar-value">¥{{ tripPlan.budget.total_meals }}</span>
        </div>
        <div class="budget-bar-divider"></div>
        <div class="budget-bar-item">
          <span class="budget-bar-icon">🚌</span>
          <span class="budget-bar-label">交通费用</span>
          <span class="budget-bar-value">¥{{ tripPlan.budget.total_transportation }}</span>
        </div>
        <div class="budget-bar-divider"></div>
        <div class="budget-bar-item budget-bar-total">
          <span class="budget-bar-icon">💰</span>
          <span class="budget-bar-label">预估总计</span>
          <span class="budget-bar-value total">¥{{ tripPlan.budget.total }}</span>
        </div>
      </div>
    </div>

    <!-- ===== 主体内容 ===== -->
    <div v-if="tripPlan" class="main-body">

      <!-- 地图容器：始终挂载在 DOM，避免 Tab 切换时找不到元素 -->
      <div class="map-wrapper" :class="{ 'map-hidden': activeTab !== 'map' }">
        <div id="amap-container" style="width: 100%; height: 560px; border-radius: 16px; overflow: hidden;"></div>
      </div>

      <!-- Tab 导航 -->
      <a-tabs v-model:activeKey="activeTab" class="main-tabs" size="large">

        <!-- Tab 1: 地图（占位，实际地图在上方常驻） -->
        <a-tab-pane key="map" tab="📍 景点地图">
          <!-- 地图已在上方渲染，此处为空 -->
        </a-tab-pane>

        <!-- Tab 2: 每日行程（Timeline 样式） -->
        <a-tab-pane key="itinerary" tab="📅 每日行程">
          <div class="itinerary-wrapper">
            <!-- 天数选择器 -->
            <div class="day-selector">
              <button
                v-for="(day, index) in tripPlan.days"
                :key="index"
                class="day-btn"
                :class="{ active: activeDay === index }"
                @click="activeDay = index"
              >
                <span class="day-btn-num">Day {{ index + 1 }}</span>
                <span class="day-btn-date">{{ day.date }}</span>
              </button>
            </div>

            <!-- 当天行程详情 -->
            <div v-if="tripPlan.days[activeDay]" class="day-detail">
              <div class="day-meta">
                <span class="day-meta-badge">第 {{ activeDay + 1 }} 天</span>
                <span class="day-meta-desc">{{ tripPlan.days[activeDay].description.replace(/^第[一二三四五六七八九十\d]+天[：:]\s*/, '') }}</span>
                <span class="day-meta-tag">🚗 {{ tripPlan.days[activeDay].transportation }}</span>
                <span class="day-meta-tag">🏨 {{ tripPlan.days[activeDay].accommodation }}</span>
              </div>

              <!-- Timeline 景点 -->
              <a-timeline class="attr-timeline">
                <a-timeline-item
                  v-for="(attr, attrIdx) in tripPlan.days[activeDay].attractions"
                  :key="attrIdx"
                  color="#e8651a"
                >
                  <div class="timeline-card">
                    <div class="timeline-card-img-wrap">
                      <img
                        :src="getAttractionImage(attr.name, attrIdx)"
                        :alt="attr.name"
                        class="timeline-card-img"
                        @error="handleImageError"
                      />
                      <div class="timeline-card-num">{{ attrIdx + 1 }}</div>
                      <div v-if="attr.ticket_price" class="timeline-card-price">¥{{ attr.ticket_price }}</div>
                    </div>
                    <div class="timeline-card-body">
                      <div class="timeline-card-title-row">
                        <h3 class="timeline-card-name">{{ attr.name }}</h3>
                        <!-- 编辑模式操作按钮 -->
                        <a-space v-if="editMode" size="small">
                          <a-button size="small" @click="moveAttraction(tripPlan.days[activeDay].day_index, attrIdx, 'up')" :disabled="attrIdx === 0">↑</a-button>
                          <a-button size="small" @click="moveAttraction(tripPlan.days[activeDay].day_index, attrIdx, 'down')" :disabled="attrIdx === tripPlan.days[activeDay].attractions.length - 1">↓</a-button>
                          <a-button size="small" danger @click="deleteAttraction(tripPlan.days[activeDay].day_index, attrIdx)">🗑️</a-button>
                        </a-space>
                      </div>

                      <!-- 查看模式 -->
                      <div v-if="!editMode" class="timeline-card-info">
                        <p class="attr-address">📌 {{ attr.address }}</p>
                        <p class="attr-desc">{{ attr.description }}</p>
                        <div class="attr-tags">
                          <span class="attr-tag">⏱ {{ attr.visit_duration }} 分钟</span>
                          <span v-if="attr.category" class="attr-tag">🏷 {{ attr.category }}</span>
                          <span v-if="attr.rating" class="attr-tag">⭐ {{ attr.rating }}</span>
                        </div>
                      </div>

                      <!-- 编辑模式 -->
                      <div v-else class="timeline-card-edit">
                        <p><strong>地址：</strong></p>
                        <a-input v-model:value="attr.address" size="small" style="margin-bottom:8px" />
                        <p><strong>游览时长（分钟）：</strong></p>
                        <a-input-number v-model:value="attr.visit_duration" :min="10" :max="480" size="small" style="width:100%;margin-bottom:8px" />
                        <p><strong>描述：</strong></p>
                        <a-textarea v-model:value="attr.description" :rows="2" size="small" />
                      </div>
                    </div>
                  </div>
                </a-timeline-item>
              </a-timeline>

              <!-- 餐饮安排 -->
              <div class="meals-section">
                <h3 class="section-title-sm">🍽️ 餐饮安排</h3>
                <div class="meals-grid">
                  <div v-for="meal in tripPlan.days[activeDay].meals" :key="meal.type" class="meal-card">
                    <div class="meal-type-icon">
                      {{ meal.type === 'breakfast' ? '🌅' : meal.type === 'lunch' ? '☀️' : meal.type === 'dinner' ? '🌙' : '🧃' }}
                    </div>
                    <div class="meal-info">
                      <span class="meal-type-label">{{ getMealLabel(meal.type) }}</span>
                      <span class="meal-name">{{ meal.name }}</span>
                      <span v-if="meal.description" class="meal-desc">{{ meal.description }}</span>
                      <span v-if="meal.estimated_cost" class="meal-cost">约 ¥{{ meal.estimated_cost }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 酒店推荐 -->
              <div v-if="tripPlan.days[activeDay].hotel" class="hotel-section">
                <h3 class="section-title-sm">🏨 住宿推荐</h3>
                <div class="hotel-card-new">
                  <div class="hotel-icon">🏨</div>
                  <div class="hotel-info">
                    <div class="hotel-name">{{ tripPlan.days[activeDay].hotel!.name }}</div>
                    <div class="hotel-meta">
                      <span>📍 {{ tripPlan.days[activeDay].hotel!.address }}</span>
                      <span>🏷 {{ tripPlan.days[activeDay].hotel!.type }}</span>
                      <span>💰 {{ tripPlan.days[activeDay].hotel!.price_range }}</span>
                      <span>⭐ {{ tripPlan.days[activeDay].hotel!.rating }}</span>
                      <span>📏 {{ tripPlan.days[activeDay].hotel!.distance }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </a-tab-pane>

        <!-- Tab 3: 天气 -->
        <a-tab-pane key="weather" tab="🌤️ 天气预报" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0">
          <div class="weather-wrapper">
            <div class="weather-grid">
              <div v-for="(w, idx) in tripPlan.weather_info" :key="idx" class="weather-tile">
                <div class="weather-tile-date">{{ w.date }}</div>
                <div class="weather-tile-icon">
                  {{ w.day_weather.includes('晴') ? '☀️' : w.day_weather.includes('云') ? '⛅' : w.day_weather.includes('雨') ? '🌧️' : '🌈' }}
                </div>
                <div class="weather-tile-temps">
                  <span class="temp-day">{{ w.day_temp }}°</span>
                  <span class="temp-sep">/</span>
                  <span class="temp-night">{{ w.night_temp }}°</span>
                </div>
                <div class="weather-tile-desc">{{ w.day_weather }}</div>
                <div class="weather-tile-wind">💨 {{ w.wind_direction }} {{ w.wind_power }}</div>
              </div>
            </div>
          </div>
        </a-tab-pane>

      </a-tabs>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🗺️</div>
      <p class="empty-text">暂无旅行计划数据，请先创建行程</p>
      <a-button type="primary" class="btn-save" @click="goBack">返回首页创建行程</a-button>
    </div>

    <!-- 回到顶部 -->
    <a-back-top :visibility-height="300">
      <div class="back-top-btn">↑</div>
    </a-back-top>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'
import { generateTripPlan } from '@/services/api'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeTab = ref('map')
const activeDay = ref(0)
let map: any = null

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    await loadAttractionPhotos()
    // 等 DOM 渲染完成后初始化地图（地图容器始终在 DOM 中）
    await nextTick()
    initMap()
  }
})

// 切换到地图 Tab 时，如果地图还没初始化则初始化
watch(activeTab, async (tab) => {
  if (tab === 'map' && !map && tripPlan.value) {
    await nextTick()
    initMap()
  }
})

const goBack = () => router.push('/')

const toggleEditMode = () => {
  editMode.value = true
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('进入编辑模式')
}

// AI 修改相关
const aiInstruction = ref('')
const aiLoading = ref(false)

const applyAiEdit = async () => {
  if (!aiInstruction.value.trim()) {
    message.warning('请输入修改要求')
    return
  }
  if (!tripPlan.value) return

  aiLoading.value = true
  try {
    // 从 sessionStorage 取原始请求参数，补充 existing_plan 和 edit_instruction
    const rawRequest = sessionStorage.getItem('tripRequest')
    const baseRequest = rawRequest ? JSON.parse(rawRequest) : {
      city: tripPlan.value.city,
      start_date: tripPlan.value.start_date,
      end_date: tripPlan.value.end_date,
      travel_days: tripPlan.value.days.length,
      transportation: '公共交通',
      accommodation: '经济型酒店',
      preferences: [],
      free_text_input: ''
    }

    const editRequest = {
      ...baseRequest,
      existing_plan: JSON.parse(JSON.stringify(tripPlan.value)),
      edit_instruction: aiInstruction.value.trim()
    }

    const result = await generateTripPlan(editRequest)
    if (result.success && result.data) {
      tripPlan.value = result.data
      sessionStorage.setItem('tripPlan', JSON.stringify(result.data))
      aiInstruction.value = ''
      message.success('AI 已更新行程')
      if (map) map.destroy()
      nextTick(() => initMap())
    } else {
      message.error('AI 修改失败，请重试')
    }
  } catch (e) {
    message.error('请求失败，请检查网络')
  } finally {
    aiLoading.value = false
  }
}

const saveChanges = () => {
  editMode.value = false
  if (tripPlan.value) sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  message.success('修改已保存')
  if (map) map.destroy()
  nextTick(() => initMap())
}

const cancelEdit = () => {
  if (originalPlan.value) tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  editMode.value = false
  message.info('已取消编辑')
}

const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return
  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) { message.warning('每天至少需要保留一个景点'); return }
  day.attractions.splice(attrIndex, 1)
  message.success('景点已删除')
}

const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return
  const attractions = tripPlan.value.days[dayIndex].attractions
  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string) => ({ breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '小吃' }[type] || type)

const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return
  const promises: Promise<void>[] = []
  tripPlan.value.days.forEach(day => {
    day.attractions.forEach(attraction => {
      const p = fetch(`http://localhost:8000/api/poi/photo?name=${encodeURIComponent(attraction.name)}`)
        .then(res => res.json())
        .then(data => { if (data.success && data.data.photo_url) attractionPhotos.value[attraction.name] = data.data.photo_url })
        .catch(() => {})
      promises.push(p)
    })
  })
  await Promise.all(promises)
}

const getAttractionImage = (name: string, index: number): string => {
  if (attractionPhotos.value[name]) return attractionPhotos.value[name]
  const colors = [
    { start: '#e8651a', end: '#c04e0e' },
    { start: '#f093fb', end: '#f5576c' },
    { start: '#4facfe', end: '#00f2fe' },
    { start: '#43e97b', end: '#38f9d7' },
    { start: '#fa709a', end: '#fee140' }
  ]
  const { start, end } = colors[index % colors.length]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220">
    <defs><linearGradient id="g${index}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${start};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${end};stop-opacity:1" />
    </linearGradient></defs>
    <rect width="400" height="220" fill="url(#g${index})"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold" fill="white">${name}</text>
  </svg>`
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="220"%3E%3Crect width="400" height="220" fill="%23f0ebe4"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="16" fill="%23a0784a"%3E暂无图片%3C/text%3E%3C/svg%3E'
}

const exportAsImage = async () => {
  try {
    message.loading({ content: '正在生成图片...', key: 'export', duration: 0 })
    const element = document.querySelector('.main-body') as HTMLElement
    if (!element) throw new Error('未找到内容元素')
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#faf6f1'
    exportContainer.style.padding = '20px'
    exportContainer.innerHTML = element.innerHTML
    const mapContainer = document.getElementById('amap-container')
    if (mapContainer && map) {
      const mapCanvas = mapContainer.querySelector('canvas')
      if (mapCanvas) {
        const snap = mapCanvas.toDataURL('image/png')
        const exportMap = exportContainer.querySelector('#amap-container')
        if (exportMap) exportMap.innerHTML = `<img src="${snap}" style="width:100%;height:100%;object-fit:cover;" />`
      }
    }
    const cardHeads = exportContainer.querySelectorAll('.ant-card-head')
    cardHeads.forEach((head) => {
      const headEl = head as HTMLElement
      headEl.style.setProperty('background-color', '#e8651a')
      headEl.style.setProperty('color', '#ffffff')
      headEl.style.setProperty('padding', '16px 24px')
      headEl.style.setProperty('font-weight', '600')
    })
    const budgetTotal = exportContainer.querySelector('.budget-bar')
    if (budgetTotal) {
      const el = budgetTotal as HTMLElement
      el.style.setProperty('background-color', '#e8651a')
      el.style.setProperty('color', '#ffffff')
    }
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)
    const canvas = await html2canvas(exportContainer, { backgroundColor: '#faf6f1', scale: 2, logging: false, useCORS: true, allowTaint: true })
    document.body.removeChild(exportContainer)
    const link = document.createElement('a')
    link.download = `旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    message.success({ content: '图片导出成功！', key: 'export' })
  } catch (error: any) {
    message.error({ content: `导出失败: ${error.message}`, key: 'export' })
  }
}

const exportAsPDF = async () => {
  try {
    message.loading({ content: '正在生成PDF...', key: 'export', duration: 0 })
    const element = document.querySelector('.main-body') as HTMLElement
    if (!element) throw new Error('未找到内容元素')
    const exportContainer = document.createElement('div')
    exportContainer.style.width = element.offsetWidth + 'px'
    exportContainer.style.backgroundColor = '#faf6f1'
    exportContainer.style.padding = '20px'
    exportContainer.innerHTML = element.innerHTML
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)
    const canvas = await html2canvas(exportContainer, { backgroundColor: '#faf6f1', scale: 2, logging: false, useCORS: true, allowTaint: true })
    document.body.removeChild(exportContainer)
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const imgWidth = 210
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }
    pdf.save(`旅行计划_${tripPlan.value?.city}_${new Date().getTime()}.pdf`)
    message.success({ content: 'PDF导出成功！', key: 'export' })
  } catch (error: any) {
    message.error({ content: `导出失败: ${error.message}`, key: 'export' })
  }
}

const initMap = async () => {
  try {
    window._AMapSecurityConfig = { securityJsCode: 'fd34e3c7f49eca5a3605ead3497d99eb' }
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow']
    })
    map = new AMap.Map('amap-container', { zoom: 12, center: [116.397128, 39.916527], viewMode: '3D' })
    addAttractionMarkers(AMap)
    message.success('地图加载成功')
  } catch {
    message.error('地图加载失败')
  }
}

const addAttractionMarkers = (AMap: any) => {
  if (!tripPlan.value) return
  const markers: any[] = []
  const allAttractions: any[] = []
  tripPlan.value.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location?.longitude && attraction.location?.latitude) {
        allAttractions.push({ ...attraction, dayIndex, attrIndex })
      }
    })
  })
  allAttractions.forEach((attraction, index) => {
    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      title: attraction.name,
      label: {
        content: `<div style="background:#e8651a;color:white;padding:4px 8px;border-radius:4px;font-size:12px;">${index + 1}</div>`,
        offset: new AMap.Pixel(0, -30)
      }
    })
    const infoWindow = new AMap.InfoWindow({
      content: `<div style="padding:10px;">
        <h4 style="margin:0 0 8px 0;">${attraction.name}</h4>
        <p style="margin:4px 0;"><strong>地址：</strong>${attraction.address}</p>
        <p style="margin:4px 0;"><strong>游览时长：</strong>${attraction.visit_duration}分钟</p>
        <p style="margin:4px 0;"><strong>描述：</strong>${attraction.description}</p>
        <p style="margin:4px 0;color:#e8651a;"><strong>第${attraction.dayIndex + 1}天 景点${attraction.attrIndex + 1}</strong></p>
      </div>`,
      offset: new AMap.Pixel(0, -30)
    })
    marker.on('click', () => infoWindow.open(map, marker.getPosition()))
    markers.push(marker)
  })
  map.add(markers)
  if (allAttractions.length > 0) map.setFitView(markers)
  drawRoutes(AMap, allAttractions)
}

const drawRoutes = (AMap: any, attractions: any[]) => {
  if (attractions.length < 2) return
  const dayGroups: any = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) dayGroups[attr.dayIndex] = []
    dayGroups[attr.dayIndex].push(attr)
  })
  Object.values(dayGroups).forEach((dayAttractions: any) => {
    if (dayAttractions.length < 2) return
    const path = dayAttractions.map((attr: any) => [attr.location.longitude, attr.location.latitude])
    map.add(new AMap.Polyline({
      path,
      strokeColor: '#e8651a',
      strokeWeight: 4,
      strokeOpacity: 0.8,
      strokeStyle: 'solid',
      showDir: true
    }))
  })
}
</script>

<style scoped>
/* ===== 整体背景 ===== */
.result-container {
  min-height: 100vh;
  background: #faf6f1;
}

/* ===== 英雄横幅 ===== */
.hero-banner {
  background: linear-gradient(135deg, #3d1f0a 0%, #7a4a28 60%, #c07840 100%);
  padding: 40px 60px 0;
  color: white;
}

.hero-content {
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 32px;
}

.hero-tag {
  display: inline-block;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  margin-bottom: 14px;
  letter-spacing: 1px;
}

.hero-city {
  font-size: 52px;
  font-weight: 800;
  margin: 0 0 10px;
  letter-spacing: 4px;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
}

.hero-dates {
  font-size: 16px;
  color: rgba(255,255,255,0.8);
  margin: 0 0 14px;
}

.hero-suggestion {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  max-width: 500px;
  line-height: 1.7;
  margin: 0;
}

.hero-right {
  padding-top: 8px;
  flex-shrink: 0;
}

/* 按钮 */
.btn-back, .btn-edit, .btn-cancel, .btn-export {
  border-radius: 8px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.35);
  color: white;
  font-size: 13px;
}

.btn-back:hover, .btn-edit:hover, .btn-cancel:hover, .btn-export:hover {
  background: rgba(255,255,255,0.25) !important;
  border-color: rgba(255,255,255,0.5) !important;
  color: white !important;
}

.btn-save {
  background: #e8651a !important;
  border-color: #e8651a !important;
  border-radius: 8px;
}

/* ===== AI 修改输入框 ===== */
.ai-edit-bar {
  max-width: 1300px;
  margin: 16px auto 0;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 12px 20px;
  backdrop-filter: blur(4px);
}

.ai-edit-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.ai-edit-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 8px !important;
  color: white !important;
}

.ai-edit-input::placeholder,
.ai-edit-input :deep(input::placeholder) {
  color: rgba(255, 255, 255, 0.6) !important;
}

.ai-edit-input :deep(input) {
  background: transparent !important;
  color: white !important;
}

.ai-edit-btn {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.25) !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
  color: white !important;
  border-radius: 8px !important;
}

.ai-edit-btn:hover {
  background: rgba(255, 255, 255, 0.35) !important;
}

/* ===== 预算条 ===== */
.budget-bar {
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.1);
  border-radius: 12px 12px 0 0;
  padding: 14px 28px;
  gap: 0;
}

.budget-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 3px;
}

.budget-bar-icon {
  font-size: 18px;
}

.budget-bar-label {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
}

.budget-bar-value {
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.budget-bar-value.total {
  font-size: 20px;
  color: #ffd580;
}

.budget-bar-total {
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 6px 16px;
}

.budget-bar-divider {
  width: 1px;
  height: 36px;
  background: rgba(255,255,255,0.2);
  margin: 0 8px;
  flex-shrink: 0;
}

/* ===== 主体 ===== */
.main-body {
  max-width: 1300px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}

/* ===== Tab 样式 ===== */
:deep(.main-tabs .ant-tabs-nav) {
  margin-bottom: 24px;
}

:deep(.main-tabs .ant-tabs-tab) {
  font-size: 15px;
  padding: 10px 20px;
  color: #a0784a;
}

:deep(.main-tabs .ant-tabs-tab-active .ant-tabs-tab-btn) {
  color: #e8651a !important;
  font-weight: 600;
}

:deep(.main-tabs .ant-tabs-ink-bar) {
  background: #e8651a;
  height: 3px;
  border-radius: 2px;
}

/* ===== 地图 ===== */
.map-wrapper {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(100, 50, 10, 0.12);
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

/* 非地图 Tab 时隐藏地图容器（但保留 DOM，避免重新初始化） */
.map-hidden {
  height: 0;
  overflow: hidden;
  margin-bottom: 0;
  box-shadow: none;
}

/* ===== 行程详情 ===== */
.itinerary-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 天数选择器 */
.day-selector {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.day-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  border: 1.5px solid #e8d5bc;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.25s ease;
  gap: 2px;
}

.day-btn:hover {
  border-color: #e8651a;
  background: #fff5ee;
}

.day-btn.active {
  border-color: #e8651a;
  background: #e8651a;
  color: white;
}

.day-btn-num {
  font-size: 14px;
  font-weight: 700;
}

.day-btn-date {
  font-size: 11px;
  opacity: 0.75;
}

/* 当天 meta 信息 */
.day-detail {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(100, 50, 10, 0.08);
}

.day-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1.5px dashed #e8d5bc;
}

.day-meta-badge {
  background: #e8651a;
  color: white;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.day-meta-desc {
  font-size: 15px;
  color: #3d1f0a;
  font-weight: 500;
  flex: 1;
}

.day-meta-tag {
  font-size: 13px;
  color: #a0784a;
  background: #faf0e6;
  padding: 3px 12px;
  border-radius: 20px;
  border: 1px solid #e8d5bc;
}

/* Timeline */
.attr-timeline {
  margin: 0;
}

:deep(.attr-timeline .ant-timeline-item-tail) {
  border-color: #e8d5bc;
}

.timeline-card {
  display: flex;
  gap: 16px;
  background: #fffaf5;
  border: 1px solid #e8d5bc;
  border-radius: 14px;
  overflow: hidden;
  transition: box-shadow 0.25s ease;
  margin-bottom: 4px;
}

.timeline-card:hover {
  box-shadow: 0 6px 20px rgba(232, 101, 26, 0.12);
}

.timeline-card-img-wrap {
  position: relative;
  flex-shrink: 0;
  width: 180px;
}

.timeline-card-img {
  width: 180px;
  height: 140px;
  object-fit: cover;
  display: block;
}

.timeline-card-num {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #e8651a;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.timeline-card-price {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(220, 50, 50, 0.88);
  color: white;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.timeline-card-body {
  flex: 1;
  padding: 14px 16px;
}

.timeline-card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.timeline-card-name {
  font-size: 17px;
  font-weight: 700;
  color: #3d1f0a;
  margin: 0;
}

.attr-address {
  font-size: 13px;
  color: #a0784a;
  margin: 0 0 6px;
}

.attr-desc {
  font-size: 14px;
  color: #5a3a20;
  line-height: 1.6;
  margin: 0 0 10px;
}

.attr-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.attr-tag {
  font-size: 12px;
  background: #fff0e6;
  border: 1px solid #f5c5a0;
  color: #c04e0e;
  padding: 2px 10px;
  border-radius: 10px;
}

.timeline-card-edit p {
  margin: 0 0 4px;
  font-size: 13px;
  color: #7a4a28;
}

/* 餐饮 */
.meals-section {
  margin-top: 28px;
}

.section-title-sm {
  font-size: 16px;
  font-weight: 700;
  color: #3d1f0a;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 4px solid #e8651a;
}

.meals-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meal-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fffaf5;
  border: 1px solid #e8d5bc;
  border-radius: 12px;
  padding: 14px 18px;
  flex: 1;
  min-width: 200px;
}

.meal-type-icon {
  font-size: 26px;
  flex-shrink: 0;
}

.meal-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.meal-type-label {
  font-size: 11px;
  color: #a0784a;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.meal-name {
  font-size: 15px;
  font-weight: 600;
  color: #3d1f0a;
}

.meal-desc {
  font-size: 13px;
  color: #7a4a28;
}

.meal-cost {
  font-size: 13px;
  color: #e8651a;
  font-weight: 600;
}

/* 酒店 */
.hotel-section {
  margin-top: 24px;
}

.hotel-card-new {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeedd 100%);
  border: 1px solid #f5c5a0;
  border-radius: 14px;
  padding: 18px 22px;
}

.hotel-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.hotel-name {
  font-size: 17px;
  font-weight: 700;
  color: #3d1f0a;
  margin-bottom: 8px;
}

.hotel-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hotel-meta span {
  font-size: 13px;
  color: #7a4a28;
  background: white;
  padding: 3px 12px;
  border-radius: 10px;
  border: 1px solid #e8d5bc;
}

/* ===== 天气 ===== */
.weather-wrapper {
  padding: 8px 0;
}

.weather-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.weather-tile {
  flex: 1;
  min-width: 140px;
  background: white;
  border: 1px solid #e8d5bc;
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  transition: all 0.25s ease;
}

.weather-tile:hover {
  box-shadow: 0 6px 20px rgba(232, 101, 26, 0.12);
  transform: translateY(-4px);
}

.weather-tile-date {
  font-size: 13px;
  color: #a0784a;
  margin-bottom: 10px;
}

.weather-tile-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.weather-tile-temps {
  font-size: 22px;
  font-weight: 700;
  color: #3d1f0a;
  margin-bottom: 6px;
}

.temp-sep {
  color: #e8d5bc;
  margin: 0 4px;
}

.temp-night {
  color: #a0784a;
  font-size: 18px;
}

.weather-tile-desc {
  font-size: 14px;
  color: #7a4a28;
  margin-bottom: 8px;
}

.weather-tile-wind {
  font-size: 12px;
  color: #a0784a;
  background: #faf0e6;
  border-radius: 10px;
  padding: 3px 10px;
  display: inline-block;
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
}

.empty-icon {
  font-size: 80px;
}

.empty-text {
  font-size: 16px;
  color: #a0784a;
}

/* ===== 回到顶部 ===== */
.back-top-btn {
  width: 46px;
  height: 46px;
  background: #e8651a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(232, 101, 26, 0.4);
  cursor: pointer;
  transition: all 0.25s ease;
}

.back-top-btn:hover {
  transform: scale(1.1);
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-banner { padding: 24px 20px 0; }
  .hero-city { font-size: 36px; }
  .hero-content { flex-direction: column; gap: 20px; }
  .budget-bar { gap: 4px; flex-wrap: wrap; }
  .main-body { padding: 20px 12px 40px; }
  .timeline-card { flex-direction: column; }
  .timeline-card-img-wrap { width: 100%; }
  .timeline-card-img { width: 100%; height: 180px; }
}
</style>
