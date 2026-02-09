<template>
  <a-modal
    v-model:visible="visible"
    :title="title"
    width="80%"
    :footer="null"
    @cancel="handleClose"
  >
    <div class="screenshot-viewer">
      <div class="screenshot-toolbar">
        <a-space>
          <a-button @click="zoomIn" :disabled="!imageUrl">
            <ZoomInOutlined /> 放大
          </a-button>
          <a-button @click="zoomOut" :disabled="!imageUrl">
            <ZoomOutOutlined /> 缩小
          </a-button>
          <a-button @click="resetZoom" :disabled="!imageUrl">
            <UndoOutlined /> 重置
          </a-button>
          <a-button @click="download" :disabled="!imageUrl">
            <DownloadOutlined /> 下载
          </a-button>
          <a-button v-if="canCompare" @click="compare" :disabled="!compareImageUrl">
            <SwapOutlined /> 对比
          </a-button>
        </a-space>
      </div>

      <div class="screenshot-content">
        <!-- 单张图片显示 -->
        <div v-if="imageUrl && !isComparing" class="single-image-container">
          <img
            :src="imageUrl"
            :style="{ transform: `scale(${zoom})` }"
            class="screenshot-image"
            @click="toggleFullscreen"
          />
          <div class="screenshot-info" v-if="currentScreenshot">
            <p><strong>步骤:</strong> {{ currentScreenshot.step_name || `步骤 ${currentScreenshot.step_index}` }}</p>
            <p v-if="currentScreenshot.is_error"><strong>错误:</strong> {{ currentScreenshot.error_message }}</p>
            <p><strong>时间:</strong> {{ formatTimestamp(currentScreenshot.timestamp) }}</p>
          </div>
        </div>

        <!-- 对比模式 -->
        <div v-else-if="isComparing" class="compare-container">
          <div class="compare-item">
            <h4>期望/基准</h4>
            <img :src="compareImageUrl" class="compare-image" />
          </div>
          <div class="compare-item">
            <h4>实际</h4>
            <img :src="imageUrl" class="compare-image" />
          </div>
        </div>

        <!-- 空状态 -->
        <a-empty v-else description="没有可显示的截图" />
      </div>

      <!-- 截图列表（如果有多个） -->
      <div v-if="screenshots.length > 1" class="screenshot-list">
        <div
          v-for="screenshot in screenshots"
          :key="screenshot.id"
          class="screenshot-thumb"
          :class="{ active: currentScreenshot?.id === screenshot.id }"
          @click="selectScreenshot(screenshot)"
        >
          <img :src="screenshot.thumbnail_path || screenshot.image_path" />
          <span v-if="screenshot.is_error" class="error-badge">错误</span>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  UndoOutlined,
  DownloadOutlined,
  SwapOutlined
} from '@ant-design/icons-vue'

interface Screenshot {
  id: number
  step_index: number
  step_name: string
  image_path: string
  thumbnail_path?: string
  is_error: boolean
  error_message?: string
  timestamp: string
}

interface Props {
  visible: boolean
  screenshots?: Screenshot[]
  initialIndex?: number
  compareWith?: Screenshot | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  screenshots: () => [],
  initialIndex: 0,
  compareWith: null
})

const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const currentScreenshot = ref<Screenshot | null>(null)
const zoom = ref(1)
const isComparing = ref(false)

const imageUrl = computed(() => {
  return currentScreenshot.value?.image_path || ''
})

const compareImageUrl = computed(() => {
  return props.compareWith?.image_path || ''
})

const canCompare = computed(() => {
  return props.compareWith !== null
})

const title = computed(() => {
  if (isComparing.value) {
    return '截图对比'
  }
  if (currentScreenshot.value) {
    return currentScreenshot.value.step_name || `步骤 ${currentScreenshot.value.step_index}`
  }
  return '截图查看'
})

watch(() => props.visible, (newVal) => {
  if (newVal && props.screenshots.length > 0) {
    selectScreenshot(props.screenshots[props.initialIndex])
  }
})

watch(() => props.initialIndex, (newIndex) => {
  if (props.screenshots[newIndex]) {
    selectScreenshot(props.screenshots[newIndex])
  }
})

function selectScreenshot(screenshot: Screenshot) {
  currentScreenshot.value = screenshot
  zoom.value = 1
}

function zoomIn() {
  zoom.value = Math.min(zoom.value + 0.25, 3)
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 0.25, 0.5)
}

function resetZoom() {
  zoom.value = 1
}

function download() {
  if (!imageUrl.value) return

  const link = document.createElement('a')
  link.href = imageUrl.value
  link.download = `screenshot_${currentScreenshot.value?.step_index || 'image'}.png`
  link.click()
  message.success('已开始下载')
}

function compare() {
  if (!canCompare.value) {
    message.warning('没有可对比的截图')
    return
  }
  isComparing.value = !isComparing.value
  resetZoom()
}

function toggleFullscreen() {
  const img = document.querySelector('.screenshot-image') as HTMLImageElement
  if (!img) return

  if (!document.fullscreenElement) {
    img.requestFullscreen().catch(err => {
      console.log('全屏失败:', err)
    })
  } else {
    document.exitFullscreen()
  }
}

function handleClose() {
  visible.value = false
  isComparing.value = false
  currentScreenshot.value = null
  zoom.value = 1
  emit('close')
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.screenshot-viewer {
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.screenshot-toolbar {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  text-align: center;
}

.screenshot-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
  background: #f5f5f5;
}

.single-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.screenshot-image {
  max-width: 100%;
  max-height: 50vh;
  object-fit: contain;
  transition: transform 0.3s ease;
  cursor: pointer;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.screenshot-image:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.screenshot-info {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-radius: 4px;
  font-size: 13px;
}

.screenshot-info p {
  margin: 4px 0;
}

.compare-container {
  display: flex;
  gap: 20px;
  width: 100%;
  justify-content: center;
}

.compare-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.compare-item h4 {
  margin-bottom: 12px;
}

.compare-image {
  max-width: 100%;
  max-height: 45vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.screenshot-list {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  overflow-x: auto;
  background: white;
}

.screenshot-thumb {
  position: relative;
  flex-shrink: 0;
  width: 80px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.screenshot-thumb:hover {
  border-color: #1890ff;
}

.screenshot-thumb.active {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.screenshot-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.error-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  padding: 2px 6px;
  background: #ff4d4f;
  color: white;
  font-size: 10px;
  border-radius: 2px;
}
</style>
