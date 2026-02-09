<template>
  <div class="driver-center">
    <div class="page-header">
      <h2>驱动中心</h2>
      <a-space>
        <a-button @click="checkAllEnvironments">
          <CheckCircleOutlined /> 检查环境
        </a-button>
      </a-space>
    </div>

    <a-row :gutter="16">
      <a-col :span="8" v-for="framework in frameworks" :key="framework.name">
        <a-card :title="framework.label" class="framework-card">
          <template #extra>
            <a-tag :color="framework.installed ? 'success' : 'default'">
              {{ framework.installed ? '已安装' : '未安装' }}
            </a-tag>
          </template>
          <div class="driver-list">
            <div
              v-for="driver in framework.drivers"
              :key="driver.id"
              class="driver-item"
            >
              <div class="driver-info">
                <div class="driver-name">{{ driver.browser_display }}</div>
                <div class="driver-version">v{{ driver.version || 'Latest' }}</div>
              </div>
              <div class="driver-actions">
                <a-button size="small" type="link" @click="showDriverDetail(driver)">
                  详情
                </a-button>
              </div>
            </div>
          </div>
          <a-divider />
          <div class="install-command">
            <div class="command-label">安装命令：</div>
            <a-typography-paragraph copyable>
              pip install {{ framework.name }}
            </a-typography-paragraph>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 驱动详情弹窗 -->
    <a-modal
      v-model:open="detailVisible"
      :title="selectedDriver?.framework_display + ' - ' + selectedDriver?.browser_display"
      width="600px"
      :footer="null"
    >
      <div v-if="selectedDriver">
        <a-descriptions bordered :column="1">
          <a-descriptions-item label="框架">
            {{ selectedDriver.framework_display }}
          </a-descriptions-item>
          <a-descriptions-item label="浏览器/平台">
            {{ selectedDriver.browser_display }}
          </a-descriptions-item>
          <a-descriptions-item label="版本">
            {{ selectedDriver.version || 'Latest' }}
          </a-descriptions-item>
          <a-descriptions-item label="下载地址">
            <a v-if="selectedDriver.download_url" :href="selectedDriver.download_url" target="_blank">
              {{ selectedDriver.download_url }}
            </a>
            <span v-else>-</span>
          </a-descriptions-item>
          <a-descriptions-item label="说明">
            {{ selectedDriver.description || '-' }}
          </a-descriptions-item>
        </a-descriptions>

        <a-divider>安装命令</a-divider>
        <a-typography-paragraph v-if="selectedDriver.install_command" copyable>
          <pre>{{ selectedDriver.install_command }}</pre>
        </a-typography-paragraph>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { CheckCircleOutlined } from '@ant-design/icons-vue'
import { get as getDriver } from '@/api/request'

const frameworks = ref([
  {
    name: 'selenium',
    label: 'Selenium',
    installed: false,
    drivers: [] as any[]
  },
  {
    name: 'playwright',
    label: 'Playwright',
    installed: false,
    drivers: [] as any[]
  },
  {
    name: 'appium',
    label: 'Appium',
    installed: false,
    drivers: [] as any[]
  }
])

const detailVisible = ref(false)
const selectedDriver = ref<any>(null)

async function loadDrivers() {
  try {
    const res = await getDriver('/drivers/')
    const drivers = res.results || res

    frameworks.value.forEach(fw => {
      fw.drivers = drivers.filter((d: any) => d.framework === fw.name)
    })
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function checkAllEnvironments() {
  const checks = frameworks.value.map(async fw => {
    try {
      const res = await post('/drivers/check_environment', { framework: fw.name })
      fw.installed = res.installed
      message.success(`${fw.label}: ${res.message}`)
    } catch (error) {
      fw.installed = false
    }
  })

  await Promise.all(checks)
}

function showDriverDetail(driver: any) {
  selectedDriver.value = driver
  detailVisible.value = true
}

async function post(url: string, data?: any) {
  return getDriver(url, data)
}

onMounted(() => {
  loadDrivers()
})
</script>

<style scoped>
.driver-center {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.framework-card {
  margin-bottom: 16px;
}

.driver-list {
  max-height: 300px;
  overflow-y: auto;
}

.driver-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.driver-info {
  flex: 1;
}

.driver-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.driver-version {
  font-size: 12px;
  color: #999;
}

.install-command {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
}

.command-label {
  font-weight: 500;
  margin-bottom: 8px;
}

.install-command pre {
  margin: 0;
  font-family: monospace;
  font-size: 12px;
}
</style>
