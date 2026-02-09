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
          :saving="saving"
          :project-id="form.project"
          :script-id="scriptId ? parseInt(scriptId) : undefined"
          :modules="modules"
          :show-type-selector="isNew && form.steps.length === 0"
          @save="handleSave"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
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
import type { ScriptForm, ScriptType, Framework } from '@/types/script'

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

// Show type modal for new scripts without type
onMounted(() => {
  loadModules()
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
      // 保存后不跳转，留在编辑页面
    }
  } catch (error) {
    // Error handled by interceptor
  } finally {
    saving.value = false
  }
}

function handleRun() {
  handleSave()
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
  margin-bottom: var(--spacing-xl);
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
  flex-shrink: 0;
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

.framework-badge {
  padding: 4px 12px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-sm);
}

.checkbox-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.editor-card {
  flex: 1;
  min-height: 600px;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
  padding: var(--spacing-xl);
}
</style>
