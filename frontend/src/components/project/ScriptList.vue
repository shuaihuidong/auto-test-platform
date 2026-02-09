<template>
  <div class="script-list-embed">
    <div class="list-header">
      <a-space>
        <span>共 {{ scripts.length }} 个脚本</span>
        <a-divider type="vertical" />
        <a-input
          v-model:value="searchText"
          placeholder="搜索脚本"
          style="width: 200px"
          allow-clear
        >
          <template #prefix><SearchOutlined /></template>
        </a-input>
        <a-select v-model:value="filterType" style="width: 120px" placeholder="类型筛选" allow-clear>
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="web">Web自动化</a-select-option>
          <a-select-option value="mobile">移动端</a-select-option>
          <a-select-option value="api">API测试</a-select-option>
        </a-select>
      </a-space>
      <a-button v-if="!embedMode" type="primary" @click="goToCreate">
        <PlusOutlined /> 新建脚本
      </a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="filteredScripts"
      :loading="loading"
      :pagination="false"
      row-key="id"
      :scroll="{ y: 500 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a-tooltip placement="top" :title="record.name">
            <a @click="goToEdit(record)" class="script-name">
              {{ record.name }}
            </a>
          </a-tooltip>
          <a-tag v-if="record.is_module" color="purple" size="small" style="margin-left: 8px">模块</a-tag>
        </template>

        <template v-else-if="column.key === 'type'">
          <a-tag :color="getTypeColor(record.type)">
            {{ getTypeLabel(record.type) }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'steps'">
          {{ record.step_count }}
        </template>

        <template v-else-if="column.key === 'updated_at'">
          {{ formatTime(record.updated_at) }}
        </template>

        <template v-else-if="column.key === 'actions'">
          <a-space :size="4">
            <a-button type="link" size="small" @click="goToEdit(record)">编辑</a-button>
            <a-button type="link" size="small" @click="runScript(record)">运行</a-button>
            <a-button type="link" size="small" @click="copyScript(record)">
              <CopyOutlined style="margin-right: 2px;" /> 复制
            </a-button>
            <a-dropdown>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="exportScript(record)">
                    <ExportOutlined /> 导出
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="deleteScript(record)" danger>
                    <DeleteOutlined /> 删除
                  </a-menu-item>
                </a-menu>
              </template>
              <a class="action-btn" @click.prevent>
                <MoreOutlined />
              </a>
            </a-dropdown>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 执行机选择对话框 -->
    <a-modal
      v-model:open="runModalVisible"
      title="选择执行机"
      width="500px"
      @ok="handleRunConfirm"
      @cancel="runModalVisible = false"
    >
      <a-form layout="vertical">
        <a-form-item label="脚本">
          <a-input :value="selectedScript?.name" disabled />
        </a-form-item>
        <a-form-item label="选择执行机">
          <a-select
            v-model:value="selectedExecutorId"
            placeholder="留空则系统自动分配"
            :loading="executorsLoading"
            allow-clear
            style="width: 100%"
          >
            <a-select-option
              v-for="executor in availableExecutors"
              :key="executor.id"
              :value="executor.id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <span>{{ executor.name }}</span>
                <a-tag
                  :color="executor.is_online ? 'success' : 'default'"
                  size="small"
                >
                  {{ executor.is_online ? '在线' : '离线' }}
                </a-tag>
              </div>
              <div style="font-size: 12px; color: #9CA3AF;">
                {{ executor.platform }} | {{ executor.scope_display }}
              </div>
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <template #extra>
            <small style="color: #6B7280;">
              如果不选择执行机，系统将自动分配给可用的执行机
            </small>
          </template>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  SearchOutlined,
  PlusOutlined,
  MoreOutlined,
  CopyOutlined,
  ExportOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { scriptApi } from '@/api/script'
import { executionApi } from '@/api/execution'
import { executorApi } from '@/api/executor'
import type { Script } from '@/types/script'
import type { Executor } from '@/api/executor'

interface Props {
  projectId: number
  embedMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  embedMode: false
})

const router = useRouter()
const loading = ref(false)
const scripts = ref<Script[]>([])
const searchText = ref('')
const filterType = ref('')

// 执行机选择相关
const runModalVisible = ref(false)
const selectedScript = ref<Script | null>(null)
const selectedExecutorId = ref<number | undefined>(undefined)
const availableExecutors = ref<Executor[]>([])
const executorsLoading = ref(false)

const columns = [
  { title: '脚本名称', key: 'name', width: 350, ellipsis: true },
  { title: '类型', key: 'type', width: 130 },
  { title: '步骤', key: 'steps', width: 110 },
  { title: '更新时间', key: 'updated_at', width: 180 },
  { title: '操作', key: 'actions', width: 250, fixed: 'right' }
]

const filteredScripts = computed(() => {
  let result = scripts.value

  if (searchText.value) {
    result = result.filter(s => s.name.toLowerCase().includes(searchText.value.toLowerCase()))
  }

  if (filterType.value) {
    result = result.filter(s => s.type === filterType.value)
  }

  return result
})

async function loadScripts() {
  loading.value = true
  try {
    const data = await scriptApi.getList(props.projectId)
    scripts.value = data.results || []
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function goToCreate() {
  // 从项目详情页来的，使用 from=project-detail
  router.push(`/script/edit?project_id=${props.projectId}&from=project-detail`)
}

function goToEdit(record: Script) {
  // 从项目详情页来的，使用 from=project-detail
  router.push(`/script/edit/${record.id}?from=project-detail`)
}

async function runScript(record: Script) {
  selectedScript.value = record
  selectedExecutorId.value = undefined
  runModalVisible.value = true

  // 加载可用执行机
  await loadExecutors()
}

async function loadExecutors() {
  executorsLoading.value = true
  try {
    const data = await executorApi.getAvailable({ project_id: props.projectId })
    availableExecutors.value = data || []
  } catch (error) {
    availableExecutors.value = []
  } finally {
    executorsLoading.value = false
  }
}

async function handleRunConfirm() {
  if (!selectedScript.value) return

  try {
    await executionApi.create({
      script_id: selectedScript.value.id,
      executor_id: selectedExecutorId.value
    })
    message.success('执行任务已创建')
    runModalVisible.value = false
    router.push('/executions')
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function copyScript(record: Script) {
  try {
    await scriptApi.duplicate(record.id)
    message.success('复制成功')
    loadScripts()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function exportScript(record: Script) {
  // TODO: 实现导出功能
  message.info('导出功能开发中')
}

function deleteScript(record: Script) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除脚本 "${record.name}" 吗？`,
    onOk: async () => {
      try {
        await scriptApi.delete(record.id)
        message.success('删除成功')
        loadScripts()
      } catch (error) {
        // 错误已由拦截器处理
      }
    }
  })
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    web: 'Web自动化',
    mobile: '移动端',
    api: 'API测试'
  }
  return labels[type] || type
}

function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    web: 'blue',
    mobile: 'green',
    api: 'orange'
  }
  return colors[type] || 'default'
}

function getFrameworkLabel(framework: string): string {
  const labels: Record<string, string> = {
    selenium: 'Selenium',
    playwright: 'Playwright',
    appium: 'Appium',
    httprunner: 'HttpRunner'
  }
  return labels[framework] || framework
}

function formatTime(time: string): string {
  const date = new Date(time)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadScripts()
})

// 暴露刷新方法给父组件
defineExpose({
  refresh: loadScripts
})
</script>

<style scoped>
.script-list-embed {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #E5E7EB;
  background: #FFFFFF;
  color: #1F2937;
}

.list-header span {
  color: #374151;
}

.script-name {
  color: #1890ff;
  cursor: pointer;
  font-weight: 500;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.script-name:hover {
  color: #40a9ff;
}

.action-btn {
  color: #374151;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

/* 优化表格列宽 */
:deep(.ant-table) {
  table-layout: fixed;
}

:deep(.ant-table-thead > tr > th) {
  padding: 12px 24px;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 12px 24px;
}

/* 操作按钮样式优化 */
:deep(.ant-btn-link) {
  padding: 4px 8px;
  height: auto;
}

/* 确保表格占满宽度 */
:deep(.ant-table-container) {
  width: 100%;
}

:deep(.ant-table-body) {
  table {
    width: 100% !important;
  }
}
</style>
