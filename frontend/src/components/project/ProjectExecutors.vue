<template>
  <div class="project-executors">
    <div class="list-header">
      <a-space>
        <span>绑定 {{ executors.length }} 台执行机</span>
      </a-space>
      <a-button type="primary" @click="showBindModal">
        <PlusOutlined /> 绑定执行机
      </a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="executors"
      :loading="loading"
      :pagination="false"
      row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <span class="status-dot" :class="record.is_online ? 'online' : 'offline'"></span>
          {{ record.name }}
        </template>

        <template v-else-if="column.key === 'owner'">
          {{ record.owner_name }}
        </template>

        <template v-else-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ record.status_display }}
          </a-tag>
          <span class="tasks-info">{{ record.current_tasks }}/{{ record.max_concurrent }}</span>
        </template>

        <template v-else-if="column.key === 'groups'">
          <a-tag v-for="group in record.groups" :key="group.id" :color="group.color">
            {{ group.name }}
          </a-tag>
          <a-tag v-for="tag in record.tags" :key="tag.id" :color="tag.color">
            {{ tag.name }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'last_heartbeat'">
          {{ record.last_heartbeat ? formatTime(record.last_heartbeat) : '-' }}
        </template>

        <template v-else-if="column.key === 'actions'">
          <a-button type="link" size="small" danger @click="unbind(record)">
            解绑
          </a-button>
        </template>
      </template>
    </a-table>

    <!-- 绑定执行机对话框 -->
    <a-modal
      v-model:open="bindModalVisible"
      title="绑定执行机"
      width="600px"
      @ok="handleBindOk"
    >
      <a-form layout="vertical">
        <a-form-item label="选择执行机">
          <a-select
            v-model:value="selectedExecutorIds"
            mode="multiple"
            placeholder="选择要绑定的执行机"
            style="width: 100%"
            :options="availableExecutors"
            :field-names="{ label: 'name', value: 'id' }"
            show-search
            :filter-option="filterOption"
          >
            <template #option="{ name, owner_name, status_display, is_online }">
              <div style="display: flex; justify-content: space-between; width: 100%">
                <span>{{ name }}</span>
                <span class="option-info">{{ owner_name }} - {{ status_display }}</span>
              </div>
            </template>
          </a-select>
          <template #extra>
            <small>只显示全局可用的执行机</small>
          </template>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { executorApi } from '@/api/executor'
import type { Executor } from '@/api/executor'

interface Props {
  projectId: number
}

const props = defineProps<Props>()

const loading = ref(false)
const executors = ref<Executor[]>([])
const availableExecutors = ref<Executor[]>([])

const bindModalVisible = ref(false)
const selectedExecutorIds = ref<number[]>([])

const columns = [
  { title: '执行机名称', key: 'name', ellipsis: true },
  { title: '所属用户', key: 'owner', width: 120 },
  { title: '状态', key: 'status', width: 150 },
  { title: '分组/标签', key: 'groups' },
  { title: '最后心跳', key: 'last_heartbeat', width: 140 },
  { title: '操作', key: 'actions', width: 80, fixed: 'right' }
]

async function loadExecutors() {
  loading.value = true
  try {
    const data = await executorApi.getList()
    // 过滤出绑定到此项目的执行机
    executors.value = data.filter(e =>
      e.bound_projects.some((p: any) => p.id === props.projectId)
    )
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

async function loadAvailableExecutors() {
  try {
    const data = await executorApi.getList({ scope: 'global', is_enabled: true })
    availableExecutors.value = data
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function showBindModal() {
  selectedExecutorIds.value = []
  loadAvailableExecutors()
  bindModalVisible.value = true
}

async function handleBindOk() {
  if (selectedExecutorIds.value.length === 0) {
    message.error('请选择执行机')
    return
  }

  loading.value = true
  try {
    // 批量绑定执行机到项目
    for (const executorId of selectedExecutorIds.value) {
      const executor = availableExecutors.value.find(e => e.id === executorId)
      if (executor) {
        await executorApi.update(executorId, {
          bound_project_ids: [...(executor.bound_projects || []), props.projectId]
        })
      }
    }
    message.success('绑定成功')
    bindModalVisible.value = false
    loadExecutors()
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

async function unbind(record: Executor) {
  const newBoundIds = record.bound_projects.filter((p: any) => p.id !== props.projectId).map((p: any) => p.id)

  try {
    await executorApi.update(record.id, { bound_project_ids: newBoundIds })
    message.success('解绑成功')
    loadExecutors()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    online: 'success',
    offline: 'default',
    busy: 'warning',
    error: 'error'
  }
  return colors[status] || 'default'
}

function formatTime(time: string): string {
  const date = new Date(time)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  return date.toLocaleString('zh-CN')
}

function filterOption(input: string, option: any): boolean {
  return option.name.toLowerCase().includes(input.toLowerCase())
}

onMounted(() => {
  loadExecutors()
})

defineExpose({
  refresh: loadExecutors
})
</script>

<style scoped>
.project-executors {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-dot.online {
  background-color: #52c41a;
}

.status-dot.offline {
  background-color: #d9d9d9;
}

.tasks-info {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}

.option-info {
  color: #999;
  font-size: 12px;
}
</style>
