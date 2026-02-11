<template>
  <div class="script-edit">
    <!-- Type Selection Modal (for new scripts) -->
    <ScriptTypeModal
      v-if="showTypeModal"
      v-model="showTypeModal"
      :default-type="form.type"
      :default-framework="form.framework"
      @confirm="handleTypeSelected"
      @cancel="handleTypeCancel"
    />

    <!-- Executor Selection Modal -->
    <a-modal
      v-model:open="showExecutorModal"
      title="选择执行机"
      :width="400"
      @ok="confirmDebug"
      @cancel="showExecutorModal = false"
    >
      <div class="executor-modal-content">
        <p class="modal-tip">请选择用于调试的执行机：</p>
        <a-select
          v-model:value="selectedExecutor"
          placeholder="请选择执行机"
          :loading="loadingExecutors"
          size="large"
          style="width: 100%"
        >
          <a-select-option
            v-for="executor in availableExecutors"
            :key="executor.id"
            :value="executor.id"
          >
            <div class="select-option-content">
              <span class="executor-name">{{ executor.name }}</span>
              <a-tag v-if="executor.is_online" color="success" size="small">在线</a-tag>
              <a-tag v-else color="default" size="small">离线</a-tag>
              <span class="executor-info">
                {{ executor.platform }} · 负载: {{ executor.current_tasks }}/{{ executor.max_concurrent }}
              </span>
            </div>
          </a-select-option>
        </a-select>
        <a-empty v-if="availableExecutors.length === 0" description="暂无可用执行机" :image-size="80" />
      </div>
    </a-modal>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <SimpleButton @click="goBack">
          <ArrowLeftOutlined /> 返回
        </SimpleButton>
        <h2>{{ isNew ? '新建脚本' : '编辑脚本' }}</h2>
      </div>
      <div class="header-right">
        <SimpleButton @click="handleSave" :loading="saving">
          <SaveOutlined /> 保存
        </SimpleButton>
      </div>
    </div>

    <div class="edit-content">
      <!-- Basic Info Card -->
      <SimpleCard class="info-card">
        <template #header>
          <div class="card-title">
            <SettingOutlined /> 基本信息
          </div>
        </template>

        <div class="info-form">
          <div class="form-group">
            <label class="form-label">脚本名称 <span class="required">*</span></label>
            <SimpleInput
              v-model="form.name"
              placeholder="请输入脚本名称"
              :error="nameError"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">脚本类型</label>
              <div class="type-display">
                <component :is="getTypeIcon(form.type)" class="type-icon" />
                <span>{{ getTypeLabel(form.type) }}</span>
                <SimpleButton
                  v-if="isNew && form.steps.length === 0"
                  variant="text"
                  size="small"
                  @click="showTypeModal = true"
                >
                  修改
                </SimpleButton>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">测试框架</label>
              <div class="framework-display">
                <span class="framework-badge">{{ form.framework }}</span>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">描述</label>
              <SimpleInput
                v-model="form.description"
                type="textarea"
                placeholder="请输入脚本描述"
                :rows="2"
              />
            </div>

            <div class="form-group">
              <label class="form-label">设为模块</label>
              <div class="checkbox-wrapper">
                <SimpleCheckbox v-model="form.is_module" label="作为模块复用" />
                <SimpleInput
                  v-if="form.is_module"
                  v-model="form.module_name"
                  placeholder="模块名称"
                  style="margin-top: 8px;"
                />
              </div>
            </div>
          </div>
        </div>
      </SimpleCard>

      <!-- Script Editor Card -->
      <div class="editor-card">
        <ScriptEditor
          v-if="!scriptTypeLoading"
          v-model="form.steps"
          :script-type="form.type"
          :framework="form.framework"
          :project-id="form.project"
          :script-id="scriptId ? parseInt(scriptId) : undefined"
          :modules="modules"
          :show-type-selector="isNew && form.steps.length === 0"
          @run="handleRun"
          @type-change="handleTypeChange"
        />
        <div v-else class="loading-container">
          <SkeletonLoader variant="custom" :count="5" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import ScriptTypeModal from '@/components/ScriptTypeModal.vue'
import ScriptEditor from '@/components/ScriptEditor/index.vue'
import SimpleButton from '@/components/ui/SimpleButton.vue'
import SimpleInput from '@/components/ui/SimpleInput.vue'
import SimpleCheckbox from '@/components/ui/SimpleCheckbox.vue'
import SimpleCard from '@/components/ui/SimpleCard.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { getScript, createScript, updateScript, getScriptModules } from '@/api/script'
import { executorApi } from '@/api/executor'
import { createExecution } from '@/api/execution'
import type { ScriptForm, ScriptType, Framework } from '@/types/script'
import type { Executor } from '@/api/executor'

const router = useRouter()
const route = useRoute()

const scriptId = route.params.id as string | undefined
const projectId = route.query.project_id as string | undefined
const from = route.query.from as string | undefined
const isNew = computed(() => !scriptId)

const saving = ref(false)
const scriptTypeLoading = ref(false)
const showTypeModal = ref(false)
const modules = ref<any[]>([])
const nameError = ref('')

// Executor related
const availableExecutors = ref<Executor[]>([])
const selectedExecutor = ref<number | null>(null)
const showExecutorModal = ref(false)
const loadingExecutors = ref(false)

// Track unsaved changes
const hasUnsavedChanges = ref(false)
let originalFormJson = ''

const form = ref<ScriptForm>({
  project: parseInt(projectId || '0'),
  name: '',
  description: '',
  type: 'web',
  framework: 'selenium',
  steps: [],
  is_module: false,
  module_name: '',
  data_driven: false
})

// Watch for form changes to track unsaved changes
watch(() => form.value, (newVal) => {
  const currentJson = JSON.stringify(newVal)
  hasUnsavedChanges.value = currentJson !== originalFormJson
}, { deep: true })

// Show type modal for new scripts without type
onMounted(() => {
  loadModules()
  loadExecutors()
  if (!isNew.value) {
    loadScript()
  } else {
    // Show type selection modal for new scripts
    showTypeModal.value = true
  }
})

async function loadScript() {
  if (!scriptId) return
  scriptTypeLoading.value = true
  try {
    const script = await getScript(parseInt(scriptId))
    form.value = {
      project: script.project,
      name: script.name,
      description: script.description,
      type: script.type,
      framework: script.framework,
      steps: script.steps,
      is_module: script.is_module,
      module_name: script.module_name || '',
      data_driven: script.data_driven
    }
    // Record original state after loading
    originalFormJson = JSON.stringify(form.value)
  } catch (error) {
    // Error handled by interceptor
  } finally {
    scriptTypeLoading.value = false
  }
}

async function loadModules() {
  try {
    const res = await getScriptModules()
    modules.value = res || []
  } catch (error) {
    console.error('Failed to load modules:', error)
    modules.value = []
  }
}

async function loadExecutors() {
  try {
    const res = await executorApi.getAvailable({ project_id: form.value.project })
    availableExecutors.value = res || []
  } catch (error) {
    console.error('Failed to load executors:', error)
    availableExecutors.value = []
  }
}

function handleTypeSelected(selection: { type: ScriptType; framework: Framework }) {
  form.value.type = selection.type
  form.value.framework = selection.framework
}

function handleTypeCancel() {
  // 用户取消选择，返回项目列表
  goBack()
}

function handleTypeChange(selection: { type: ScriptType; framework: Framework }) {
  form.value.type = selection.type
  form.value.framework = selection.framework
  showTypeModal.value = true
}

function goBack() {
  console.log('[ScriptEdit] goBack called, from:', from, 'project:', form.value.project)
  // 根据 from 参数决定返回到哪里
  if (from === 'all') {
    // 从所有脚本页面来的，返回到所有脚本
    console.log('[ScriptEdit] Returning to all scripts')
    router.push('/scripts')
  } else if (from === 'project-detail' && form.value.project) {
    // 从项目详情页（嵌入模式）来的，返回到项目详情页
    console.log('[ScriptEdit] Returning to project detail:', form.value.project)
    router.push(`/projects/${form.value.project}`)
  } else if ((from === 'project-list' || from === 'project') && form.value.project) {
    // 从项目脚本列表来的，返回到项目详情页（因为用户是从项目管理进入的）
    console.log('[ScriptEdit] Returning to project detail:', form.value.project)
    router.push(`/projects/${form.value.project}`)
  } else if (form.value.project) {
    // 默认返回到项目详情页
    console.log('[ScriptEdit] Returning to default project detail:', form.value.project)
    router.push(`/projects/${form.value.project}`)
  } else {
    console.log('[ScriptEdit] Returning to projects list')
    router.push('/projects')
  }
}

async function handleSave() {
  if (!form.value.name) {
    nameError.value = '请输入脚本名称'
    message.error('请输入脚本名称')
    return
  }

  nameError.value = ''

  saving.value = true
  try {
    if (isNew.value) {
      await createScript(form.value)
      message.success('创建成功')
      goBack() // 新建脚本后返回列表
    } else {
      await updateScript(parseInt(scriptId!), form.value)
      message.success('保存成功')
      // Update original state after saving
      originalFormJson = JSON.stringify(form.value)
      hasUnsavedChanges.value = false
    }
  } catch (error) {
    // Error handled by interceptor
  } finally {
    saving.value = false
  }
}

async function handleRun() {
  // 验证脚本名称
  if (!form.value.name) {
    nameError.value = '请输入脚本名称'
    message.error('请输入脚本名称')
    return
  }

  // 检查是否有未保存的修改
  if (hasUnsavedChanges.value) {
    Modal.confirm({
      title: '有未保存的修改',
      content: '脚本有未保存的修改，是否先保存后再调试？',
      okText: '保存并调试',
      cancelText: '取消',
      onOk: async () => {
        await handleSave()
        await showExecutorSelector()
      }
    })
    return
  }

  // 如果是新建脚本，需要先保存
  if (isNew.value) {
    Modal.confirm({
      title: '保存新脚本',
      content: '调试需要先保存脚本，是否立即保存？',
      okText: '保存并调试',
      cancelText: '取消',
      onOk: async () => {
        await handleSave()
        await showExecutorSelector()
      }
    })
    return
  }

  // 已保存的脚本，直接显示执行机选择
  await showExecutorSelector()
}

async function showExecutorSelector() {
  // 重新加载执行机列表
  loadingExecutors.value = true
  await loadExecutors()
  loadingExecutors.value = false

  // 检查是否有可用执行机
  if (availableExecutors.value.length === 0) {
    message.warning('暂无可用执行机，请先添加并启动执行机')
    return
  }

  // 显示执行机选择对话框
  selectedExecutor.value = null
  showExecutorModal.value = true
}

async function confirmDebug() {
  if (!selectedExecutor.value) {
    message.error('请选择执行机')
    return
  }

  const currentScriptId = scriptId ? parseInt(scriptId) : (await createScript(form.value)).id

  try {
    await createExecution({
      script_id: currentScriptId,
      executor_id: selectedExecutor.value
    })
    message.success('调试任务已创建')
    showExecutorModal.value = false

    // 跳转到执行记录页面
    router.push('/executions')
  } catch (error) {
    console.error('Failed to create execution:', error)
  }
}

function getTypeLabel(type: ScriptType): string {
  const labels: Record<ScriptType, string> = {
    web: 'Web自动化',
    mobile: '移动端',
    api: 'API测试'
  }
  return labels[type]
}

function getTypeIcon(type: ScriptType) {
  // Would return appropriate icon component
  return null
}
</script>

<style scoped>
.script-edit {
  max-width: 1600px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.page-header h2 {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.edit-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.info-card {
}

.card-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.required {
  color: var(--color-error);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.type-display,
.framework-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
}

.type-icon {
  font-size: 18px;
  color: var(--color-primary);
}

.type-display span {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.framework-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #ffffff;
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-radius: var(--radius-sm);
  box-shadow: 0 1px 3px rgba(24, 144, 255, 0.3);
}

.checkbox-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.editor-card {
  min-height: 800px;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
  padding: var(--spacing-xl);
}

/* Executor Modal */
.executor-modal-content {
  padding: var(--spacing-md) 0;
}

.modal-tip {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-secondary);
}

.select-option-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 4px 0;
  width: 100%;
}

.select-option-content .executor-name {
  font-size: 13px;
  color: #666;
}

.select-option-content .executor-info {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}
</style>
