<template>
  <div class="executor-manage">
    <div class="page-header">
      <h2>执行机管理</h2>
      <a-space>
        <a-button @click="showGroupModal">
          <AppstoreOutlined /> 分组管理
        </a-button>
        <a-button @click="showTagModal">
          <TagsOutlined /> 标签管理
        </a-button>
        <a-button type="primary" @click="showCreateModal">
          <PlusOutlined /> 手动添加执行机
        </a-button>
      </a-space>
    </div>

    <!-- 筛选条件 -->
    <a-card class="filter-card">
      <a-form layout="inline">
        <a-form-item label="状态">
          <a-select v-model:value="filters.status" style="width: 120px" allow-clear @change="loadExecutors">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="online">在线</a-select-option>
            <a-select-option value="offline">离线</a-select-option>
            <a-select-option value="busy">忙碌</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="作用域">
          <a-select v-model:value="filters.scope" style="width: 120px" allow-clear @change="loadExecutors">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="global">全局</a-select-option>
            <a-select-option value="project">项目专用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="平台">
          <a-select v-model:value="filters.platform" style="width: 120px" allow-clear @change="loadExecutors">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="Windows">Windows</a-select-option>
            <a-select-option value="Mac">Mac</a-select-option>
            <a-select-option value="Linux">Linux</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 执行机列表 -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="executors"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="executor-name">
              <span class="status-dot" :class="record.is_online ? 'online' : 'offline'"></span>
              <strong>{{ record.name }}</strong>
            </div>
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

          <template v-else-if="column.key === 'scope'">
            <a-tag :color="record.scope === 'global' ? 'blue' : 'green'">
              {{ record.scope_display }}
            </a-tag>
          </template>

          <template v-else-if="column.key === 'platform'">
            {{ record.platform || '-' }}
          </template>

          <template v-else-if="column.key === 'groups'">
            <a-tag v-for="group in record.groups" :key="group.id" :color="group.color" class="group-tag">
              {{ group.name }}
            </a-tag>
            <a-tag v-for="tag in record.tags" :key="tag.id" :color="tag.color" class="tag-tag">
              {{ tag.name }}
            </a-tag>
          </template>

          <template v-else-if="column.key === 'last_heartbeat'">
            {{ record.last_heartbeat ? formatTime(record.last_heartbeat) : '-' }}
          </template>

          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
              <a-button type="link" size="small" @click="editExecutor(record)">编辑</a-button>
              <a-popconfirm
                title="确定要删除此执行机吗？"
                @confirm="deleteExecutor(record.id)"
              >
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 创建/编辑执行机对话框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑执行机' : '手动添加执行机'"
      width="600px"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <a-alert
        message="提示"
        description="执行机客户端连接服务器后会自动注册，通常不需要手动添加。手动添加仅用于特殊场景。"
        type="info"
        show-icon
        style="margin-bottom: 16px"
      />
      <a-form :model="form" layout="vertical">
        <a-form-item label="执行机名称" required>
          <a-input v-model:value="form.name" placeholder="如：家里电脑、公司电脑" />
        </a-form-item>

        <a-form-item label="作用域">
          <a-radio-group v-model:value="form.scope">
            <a-radio value="global">全局可用</a-radio>
            <a-radio value="project">项目专用</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item v-if="form.scope === 'project'" label="绑定项目">
          <a-select
            v-model:value="form.bound_project_ids"
            mode="multiple"
            placeholder="选择绑定的项目"
            style="width: 100%"
          >
            <a-select-option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="最大并发数">
          <a-input-number v-model:value="form.max_concurrent" :min="1" :max="10" style="width: 150px" />
        </a-form-item>

        <a-form-item label="分组">
          <a-select
            v-model:value="form.group_ids"
            mode="multiple"
            placeholder="选择分组"
            style="width: 100%"
          >
            <a-select-option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="标签">
          <a-select
            v-model:value="form.tag_ids"
            mode="multiple"
            placeholder="选择标签"
            style="width: 100%"
          >
            <a-select-option v-for="tag in tags" :key="tag.id" :value="tag.id">
              {{ tag.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" :rows="3" placeholder="执行机描述" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 分组管理对话框 -->
    <a-modal
      v-model:open="groupModalVisible"
      title="分组管理"
      width="600px"
      @ok="handleGroupModalOk"
    >
      <a-button type="dashed" block @click="addGroup" style="margin-bottom: 16px">
        <PlusOutlined /> 添加分组
      </a-button>
      <a-list :data-source="groups" bordered>
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <a-input
                  v-if="item.editing"
                  v-model:value="item.newName"
                  size="small"
                  @blur="saveGroup(item)"
                  @keyup.enter="saveGroup(item)"
                />
                <span v-else>{{ item.name }}</span>
              </template>
              <template #description>
                <div v-if="item.editing">
                  <color-picker v-model:value="item.newColor" size="small" />
                </div>
                <a-tag v-else :color="item.color">{{ item.color }}</a-tag>
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-button v-if="!item.editing" type="link" size="small" @click="editGroup(item)">编辑</a-button>
              <a-button v-else type="link" size="small" @click="saveGroup(item)">保存</a-button>
              <a-popconfirm title="确定删除?" @confirm="deleteGroup(item.id)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-modal>

    <!-- 标签管理对话框 -->
    <a-modal
      v-model:open="tagModalVisible"
      title="标签管理"
      width="600px"
      @ok="handleTagModalOk"
    >
      <a-button type="dashed" block @click="addTag" style="margin-bottom: 16px">
        <PlusOutlined /> 添加标签
      </a-button>
      <a-list :data-source="tags" bordered>
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <a-input
                  v-if="item.editing"
                  v-model:value="item.newName"
                  size="small"
                  @blur="saveTag(item)"
                  @keyup.enter="saveTag(item)"
                />
                <span v-else>{{ item.name }}</span>
              </template>
              <template #description>
                <a-tag v-if="!item.editing" :color="item.color">{{ item.color }}</a-tag>
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-button v-if="!item.editing" type="link" size="small" @click="editTag(item)">编辑</a-button>
              <a-button v-else type="link" size="small" @click="saveTag(item)">保存</a-button>
              <a-popconfirm title="确定删除?" @confirm="deleteTag(item.id)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-modal>

    <!-- 详情对话框 -->
    <a-modal
      v-model:open="detailVisible"
      title="执行机详情"
      width="800px"
      :footer="null"
    >
      <a-descriptions v-if="currentExecutor" :column="2" bordered>
        <a-descriptions-item label="名称">{{ currentExecutor.name }}</a-descriptions-item>
        <a-descriptions-item label="UUID">{{ currentExecutor.uuid }}</a-descriptions-item>
        <a-descriptions-item label="所属用户">{{ currentExecutor.owner_name }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(currentExecutor.status)">
            {{ currentExecutor.status_display }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="作用域">
          <a-tag :color="currentExecutor.scope === 'global' ? 'blue' : 'green'">
            {{ currentExecutor.scope_display }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="平台">{{ currentExecutor.platform }}</a-descriptions-item>
        <a-descriptions-item label="并发数">
          {{ currentExecutor.current_tasks }} / {{ currentExecutor.max_concurrent }}
        </a-descriptions-item>
        <a-descriptions-item label="最后心跳">
          {{ currentExecutor.last_heartbeat ? formatTime(currentExecutor.last_heartbeat) : '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="浏览器" :span="2">
          <a-tag v-for="browser in currentExecutor.browser_types" :key="browser" color="cyan">
            {{ browser }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="分组" :span="2">
          <a-tag v-for="group in currentExecutor.groups" :key="group.id" :color="group.color">
            {{ group.name }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="标签" :span="2">
          <a-tag v-for="tag in currentExecutor.tags" :key="tag.id" :color="tag.color">
            {{ tag.name }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">
          {{ currentExecutor.description || '-' }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { AppstoreOutlined, TagsOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { executorApi, executorGroupApi, executorTagApi } from '@/api/executor'
import type { Executor, ExecutorGroup, ExecutorTag } from '@/api/executor'
import { projectApi } from '@/api/project'

interface FormState {
  id?: number
  name: string
  scope: string
  max_concurrent: number
  group_ids: number[]
  tag_ids: number[]
  bound_project_ids: number[]
  description: string
}

const columns = [
  { title: '执行机名称', key: 'name', width: 200 },
  { title: '所属用户', key: 'owner', width: 120 },
  { title: '状态', key: 'status', width: 150 },
  { title: '作用域', key: 'scope', width: 120 },
  { title: '平台', key: 'platform', width: 100 },
  { title: '分组/标签', key: 'groups' },
  { title: '最后心跳', key: 'last_heartbeat', width: 160 },
  { title: '操作', key: 'actions', width: 160, fixed: 'right' }
]

const loading = ref(false)
const executors = ref<Executor[]>([])
const groups = ref<ExecutorGroup[]>([])
const tags = ref<ExecutorTag[]>([])
const projects = ref<any[]>([])

const filters = reactive({
  status: '',
  scope: '',
  platform: ''
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// 表单
const modalVisible = ref(false)
const isEdit = ref(false)
const form = reactive<FormState>({
  name: '',
  scope: 'global',
  max_concurrent: 3,
  group_ids: [],
  tag_ids: [],
  bound_project_ids: [],
  description: ''
})

// 分组管理
const groupModalVisible = ref(false)

// 标签管理
const tagModalVisible = ref(false)

// 详情
const detailVisible = ref(false)
const currentExecutor = ref<Executor | null>(null)

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
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return date.toLocaleString('zh-CN')
}

async function loadExecutors() {
  loading.value = true
  try {
    const res = await executorApi.getList(filters) as any
    executors.value = res.results || res || []
    pagination.total = res.count || res.length || 0
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

async function loadGroups() {
  try {
    const res = await executorGroupApi.getList() as any
    groups.value = res.results || res || []
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function loadTags() {
  try {
    const res = await executorTagApi.getList() as any
    tags.value = res.results || res || []
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function loadProjects() {
  try {
    const res = await projectApi.getList()
    projects.value = res.results || []
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function showCreateModal() {
  isEdit.value = false
  Object.assign(form, {
    name: '',
    scope: 'global',
    max_concurrent: 3,
    group_ids: [],
    tag_ids: [],
    bound_project_ids: [],
    description: ''
  })
  modalVisible.value = true
}

function editExecutor(record: Executor) {
  isEdit.value = true
  Object.assign(form, {
    id: record.id,
    name: record.name,
    scope: record.scope,
    max_concurrent: record.max_concurrent,
    group_ids: record.groups.map(g => g.id),
    tag_ids: record.tags.map(t => t.id),
    bound_project_ids: record.bound_projects.map(p => p.id),
    description: record.description
  })
  modalVisible.value = true
}

async function handleSubmit() {
  if (!form.name) {
    message.error('请输入执行机名称')
    return
  }

  loading.value = true
  try {
    if (isEdit.value && form.id) {
      await executorApi.update(form.id, form)
      message.success('更新成功')
    } else {
      await executorApi.create(form)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadExecutors()
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  modalVisible.value = false
}

async function deleteExecutor(id: number) {
  try {
    await executorApi.delete(id)
    message.success('删除成功')
    loadExecutors()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function viewDetail(record: Executor) {
  currentExecutor.value = record
  detailVisible.value = true
}

// 分组管理
function showGroupModal() {
  groupModalVisible.value = true
}

function addGroup() {
  const newGroup: ExecutorGroup & { editing?: boolean; newName?: string; newColor?: string } = {
    id: 0,
    name: '',
    description: '',
    color: '#1890ff',
    sort_order: groups.value.length,
    editing: true,
    newName: '',
    newColor: '#1890ff'
  }
  groups.value.push(newGroup)
}

function editGroup(group: ExecutorGroup & { editing?: boolean }) {
  group.editing = true
  group.newName = group.name
  group.newColor = group.color
}

async function saveGroup(group: ExecutorGroup & { editing?: boolean; newName?: string; newColor?: string }) {
  if (!group.newName) {
    message.error('请输入分组名称')
    return
  }

  try {
    if (group.id) {
      // 更新
      await executorGroupApi.update(group.id, {
        name: group.newName,
        color: group.newColor
      })
      message.success('更新成功')
    } else {
      // 创建
      const newGroup = await executorGroupApi.create({
        name: group.newName,
        color: group.newColor,
        sort_order: groups.value.length
      })
      // 更新本地数据
      const index = groups.value.findIndex(g => g === group)
      if (index !== -1) {
        groups.value[index] = { ...newGroup, ...group, id: newGroup.id }
      }
      message.success('创建成功')
    }
    await loadGroups()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function deleteGroup(id: number) {
  try {
    await executorGroupApi.delete(id)
    message.success('删除成功')
    loadGroups()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function handleGroupModalOk() {
  // 过滤掉未保存的新增项
  groups.value = groups.value.filter(g => g.id !== 0)
  groupModalVisible.value = false
}

// 标签管理
function showTagModal() {
  tagModalVisible.value = true
}

function addTag() {
  const newTag: ExecutorTag & { editing?: boolean; newName?: string; newColor?: string } = {
    id: 0,
    name: '',
    color: '#52c41a',
    sort_order: tags.value.length,
    editing: true,
    newName: '',
    newColor: '#52c41a'
  }
  tags.value.push(newTag)
}

function editTag(tag: ExecutorTag & { editing?: boolean }) {
  tag.editing = true
  tag.newName = tag.name
  tag.newColor = tag.color
}

async function saveTag(tag: ExecutorTag & { editing?: boolean; newName?: string; newColor?: string }) {
  if (!tag.newName) {
    message.error('请输入标签名称')
    return
  }

  try {
    if (tag.id) {
      await executorTagApi.update(tag.id, {
        name: tag.newName,
        color: tag.newColor
      })
      message.success('更新成功')
    } else {
      const newTag = await executorTagApi.create({
        name: tag.newName,
        color: tag.newColor,
        sort_order: tags.value.length
      })
      const index = tags.value.findIndex(t => t === tag)
      if (index !== -1) {
        tags.value[index] = { ...newTag, ...tag, id: newTag.id }
      }
      message.success('创建成功')
    }
    await loadTags()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

async function deleteTag(id: number) {
  try {
    await executorTagApi.delete(id)
    message.success('删除成功')
    loadTags()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function handleTagModalOk() {
  tags.value = tags.value.filter(t => t.id !== 0)
  tagModalVisible.value = false
}

function handleTableChange() {
  // 处理表格分页变化
}

onMounted(() => {
  loadExecutors()
  loadGroups()
  loadTags()
  loadProjects()
})
</script>

<style scoped>
.executor-manage {
  max-width: 1600px;
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

.filter-card {
  margin-bottom: 16px;
}

.executor-name {
  display: flex;
  align-items: center;
}

.status-dot {
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

.group-tag,
.tag-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}
</style>
