<template>
  <div class="script-editor">
    <!-- Header Toolbar -->
    <div class="editor-header">
      <div class="header-left">
        <SimpleButton
          v-if="showTypeSelector"
          variant="default"
          size="small"
          @click="handleTypeChange"
        >
          <SettingOutlined />
          重新选择类型
        </SimpleButton>
        <div v-else class="type-info">
          <component :is="getTypeIcon(scriptType)" class="type-icon" />
          <span>{{ getTypeLabel(scriptType) }}</span>
          <span class="framework-badge">{{ getFrameworkLabel(framework) }}</span>
        </div>
      </div>

      <div class="header-center">
        <div class="mode-switch">
          <button
            :class="['mode-btn', { active: editorMode === 'visual' }]"
            @click="editorMode = 'visual'"
          >
            可视化模式
          </button>
          <button
            :class="['mode-btn', { active: editorMode === 'json' }]"
            @click="editorMode = 'json'"
          >
            JSON模式
          </button>
        </div>
      </div>

      <div class="header-right">
        <span class="step-count">步骤数: {{ steps.length }}</span>
        <SimpleButton variant="default" @click="handleClear">
          <ClearOutlined />
          清空
        </SimpleButton>
        <SimpleButton variant="default" @click="undo" :disabled="!canUndo">
          <UndoOutlined />
        </SimpleButton>
        <SimpleButton variant="default" @click="redo" :disabled="!canRedo">
          <RedoOutlined />
        </SimpleButton>
        <SimpleButton @click="$emit('save')" :loading="saving">
          <SaveOutlined />
          保存
        </SimpleButton>
        <SimpleButton variant="primary" @click="$emit('run')">
          <PlayCircleOutlined />
          运行
        </SimpleButton>
      </div>
    </div>

    <!-- Three Column Layout -->
    <div class="editor-body">
      <!-- Left: Step Palette -->
      <div class="step-palette">
        <div v-for="category in stepCategories" :key="category.name" class="step-category">
          <div class="category-title">
            <component :is="category.icon" class="category-icon" />
            {{ category.label }}
          </div>
          <div class="category-items">
            <StepCard
              v-for="step in category.steps"
              :key="step.type"
              :label="step.label"
              :icon="step.icon"
              :description="step.description"
              @dragstart="handleDragStart($event, step)"
            />
          </div>
        </div>
      </div>

      <!-- Center: Canvas Area -->
      <div class="canvas-area" @drop="handleDrop" @dragover.prevent>
        <!-- Visual Mode -->
        <div v-if="editorMode === 'visual'" class="canvas-content">
          <EmptyState
            v-if="steps.length === 0"
            icon="inbox"
            title="画布为空"
            message="将左侧步骤拖拽至此开始编排测试用例"
            size="large"
          >
            <template #action>
              <SimpleButton variant="primary" @click="showHelp">
                查看帮助
              </SimpleButton>
            </template>
          </EmptyState>

          <draggable
            v-else
            v-model="localSteps"
            item-key="id"
            handle=".canvas-step__handle"
            @end="handleDragEnd"
          >
            <template #item="{ element: step }">
              <CanvasStep
                :step="step"
                :selected="selectedStepId === step.id"
                @click="selectStep(step)"
                @copy="copyStep"
                @delete="removeStep"
              />
            </template>
          </draggable>
        </div>

        <!-- JSON Mode -->
        <div v-else class="json-editor-container">
          <textarea
            v-model="jsonContent"
            class="json-editor"
            placeholder='{"steps": [...]}'
            @blur="syncFromJson"
          />
          <div v-if="jsonError" class="json-error">
            {{ jsonError }}
          </div>
        </div>
      </div>

      <!-- Right: Property Panel -->
      <div class="property-panel">
        <div class="panel-header">
          <h4>步骤属性</h4>
          <SimpleButton
            v-if="selectedStep"
            variant="text"
            size="small"
            @click="clearSelection"
          >
            <CloseOutlined />
          </SimpleButton>
        </div>

        <div class="panel-body">
          <!-- Variable Selector (shown when active) -->
          <div v-if="variableSelectorVisible" class="variable-selector">
            <div class="variable-header">
              <span><DatabaseOutlined /> 选择变量</span>
              <SimpleButton variant="text" size="small" @click="variableSelectorVisible = false">
                <CloseOutlined />
              </SimpleButton>
            </div>
            <div class="variable-list">
              <div v-if="projectVariables.length > 0" class="variable-group">
                <div class="variable-group-title">项目变量</div>
                <div
                  v-for="variable in projectVariables"
                  :key="variable.id"
                  class="variable-item"
                  @click="insertVariable(variable)"
                >
                  <span class="var-name">{{ variable.name }}</span>
                  <span class="var-type">{{ variable.type_display }}</span>
                  <span class="var-preview">: {{ formatVariablePreview(variable) }}</span>
                </div>
              </div>
              <div v-if="scriptVariables.length > 0" class="variable-group">
                <div class="variable-group-title">脚本变量</div>
                <div
                  v-for="variable in scriptVariables"
                  :key="variable.id"
                  class="variable-item"
                  @click="insertVariable(variable)"
                >
                  <span class="var-name">{{ variable.name }}</span>
                  <span class="var-type">{{ variable.type_display }}</span>
                  <span class="var-preview">: {{ formatVariablePreview(variable) }}</span>
                </div>
              </div>
              <EmptyState
                v-if="projectVariables.length === 0 && scriptVariables.length === 0"
                icon="database"
                message="暂无变量"
                size="small"
              />
            </div>
          </div>

          <!-- Step Form -->
          <PropertyForm
            v-if="selectedStep"
            :step="selectedStep"
            :param-schemas="getParamSchemas(selectedStep.type)"
            @update:step="updateStep"
            @showVariableSelector="showVariableSelectorFor"
          />

          <!-- Empty State -->
          <EmptyState
            v-else
            icon="setting"
            message="请在画布中选择步骤以编辑属性"
            size="medium"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import draggable from 'vuedraggable'

// Icons
import {
  SettingOutlined,
  ClearOutlined,
  UndoOutlined,
  RedoOutlined,
  SaveOutlined,
  PlayCircleOutlined,
  CloseOutlined,
  DatabaseOutlined
} from '@ant-design/icons-vue'

// Components
import SimpleButton from '@/components/ui/SimpleButton.vue'
import StepCard from '@/components/ui/StepCard.vue'
import CanvasStep from '@/components/ui/CanvasStep.vue'
import PropertyForm from '@/components/ui/PropertyForm.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

// Types & Config
import type { TestStep, ScriptType, Framework, StepType } from '@/types/script-editor'
import { getStepCategories, getDefaultParams } from '@/config/steps'
import type { StepDefinition, Variable } from '@/types/script-editor'

interface Props {
  modelValue: TestStep[]
  scriptType: ScriptType
  framework: Framework
  saving?: boolean
  projectId?: number
  scriptId?: number
  modules?: any[]
  showTypeSelector?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: TestStep[]): void
  (e: 'save'): void
  (e: 'run'): void
  (e: 'typeChange', selection: { type: ScriptType; framework: Framework }): void
}

const props = withDefaults(defineProps<Props>(), {
  saving: false,
  modules: () => [],
  showTypeSelector: false
})

const emit = defineEmits<Emits>()

// Local state
const localSteps = ref<TestStep[]>([...props.modelValue])
const selectedStepId = ref<string | null>(null)
const selectedStep = ref<TestStep | null>(null)
const editorMode = ref<'visual' | 'json'>('visual')
const jsonContent = ref('')
const jsonError = ref('')

// Track external updates to prevent overriding local edits
const lastExternalUpdate = ref<number>(Date.now())

// History for undo/redo
const historyStack = ref<TestStep[][]>([])
const historyIndex = ref(-1)
const maxHistorySize = 50

// Clipboard
const clipboard = ref<TestStep | null>(null)

// Variable selector
const variableSelectorVisible = ref(false)
const projectVariables = ref<Variable[]>([])
const scriptVariables = ref<Variable[]>([])
const currentInsertField = ref<string>('')

// Computed properties
const steps = computed({
  get: () => localSteps.value,
  set: (value) => {
    localSteps.value = value
    isLocalUpdate = true  // Mark this as a local update
    emit('update:modelValue', value)
  }
})

const stepCategories = computed(() => {
  return getStepCategories(props.scriptType)
})

const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < historyStack.value.length - 1)

// Watch for external changes (only when script is first loaded or externally updated)
let isInitializing = true
let lastKnownValue = JSON.stringify(props.modelValue)
let isLocalUpdate = false  // Track if we're causing the update

watch(() => props.modelValue, (newValue, oldValue) => {
  const newValueStr = JSON.stringify(newValue)

  // Skip if this is an update we caused ourselves
  if (isLocalUpdate) {
    isLocalUpdate = false
    lastKnownValue = newValueStr
    return
  }

  // Only update if the value actually changed (not just a reference change)
  if (newValueStr !== lastKnownValue) {
    // During initialization, just sync
    if (isInitializing) {
      localSteps.value = [...newValue]
      lastKnownValue = newValueStr
      isInitializing = false
    } else {
      // After initialization, only sync if the content is meaningfully different
      // This handles external updates (e.g., from server) without overwriting local edits
      // We need to check if this is a true external change
      if (JSON.stringify(localSteps.value) !== newValueStr) {
        localSteps.value = [...newValue]
        lastKnownValue = newValueStr
      }
    }
  }
}, { deep: true })

// Don't watch steps for history - it causes too many issues
// History will be added manually on important actions instead
// Remove the automatic history watch to prevent state reset issues

// Watch editor mode changes
watch(editorMode, (newMode) => {
  if (newMode === 'json') {
    jsonContent.value = JSON.stringify({ steps: steps.value }, null, 2)
    jsonError.value = ''
  } else {
    syncFromJson()
  }
})

// Methods
function selectStep(step: TestStep) {
  selectedStepId.value = step.id
  selectedStep.value = step
}

function clearSelection() {
  selectedStepId.value = null
  selectedStep.value = null
}

function updateStep(step: TestStep) {
  const index = steps.value.findIndex(s => s.id === step.id)
  if (index !== -1) {
    // Create a new array reference to trigger reactivity
    const newSteps = [...steps.value]
    newSteps[index] = step
    steps.value = newSteps // This will trigger the computed setter and emit to parent

    if (selectedStepId.value === step.id) {
      selectedStep.value = step
    }
  }
}

function handleDragStart(event: DragEvent, stepDef: StepDefinition) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify({
      type: stepDef.type,
      label: stepDef.label
    }))
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  const data = event.dataTransfer?.getData('application/json')
  if (!data) return

  const stepData = JSON.parse(data)
  const newStep: TestStep = {
    id: `step_${Date.now()}`,
    type: stepData.type,
    name: stepData.label,
    params: getDefaultParams(stepData.type, props.scriptType)
  }

  steps.value = [...steps.value, newStep]
  selectStep(newStep)
}

function handleDragEnd() {
  // After drag completes, sync with parent through emit
  // This ensures parent has the latest order
  const currentSteps = [...localSteps.value]
  isLocalUpdate = true  // Mark this as a local update
  emit('update:modelValue', currentSteps)
  message.success('步骤顺序已更新')
}

function removeStep(step: TestStep) {
  steps.value = steps.value.filter(s => s.id !== step.id)
  if (selectedStepId.value === step.id) {
    clearSelection()
  }
}

function copyStep(step: TestStep) {
  clipboard.value = JSON.parse(JSON.stringify(step))
  const newStep: TestStep = {
    ...clipboard.value,
    id: `step_${Date.now()}`,
    name: `${clipboard.value.name} (副本)`
  }
  const index = steps.value.findIndex(s => s.id === step.id)
  steps.value.splice(index + 1, 0, newStep)
  selectStep(newStep)
  message.success('步骤已复制')
}

function handleClear() {
  if (steps.value.length === 0) return

  Modal.confirm({
    title: '清空画布',
    content: '确定要清空所有步骤吗？此操作不可撤销。',
    okText: '确认清空',
    cancelText: '取消',
    onOk: () => {
      steps.value = []
      clearSelection()
      message.success('画布已清空')
    }
  })
}

function handleTypeChange() {
  if (steps.value.length > 0) {
    Modal.confirm({
      title: '切换测试类型',
      content: '切换类型将清空当前画布，是否继续？',
      okText: '确认切换',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => {
        emit('typeChange', { type: props.scriptType, framework: props.framework })
      }
    })
  } else {
    emit('typeChange', { type: props.scriptType, framework: props.framework })
  }
}

function undo() {
  if (canUndo.value) {
    historyIndex.value--
    steps.value = JSON.parse(JSON.stringify(historyStack.value[historyIndex.value]))
    clearSelection()
    message.success('已撤销')
  }
}

function redo() {
  if (canRedo.value) {
    historyIndex.value++
    steps.value = JSON.parse(JSON.stringify(historyStack.value[historyIndex.value]))
    clearSelection()
    message.success('已重做')
  }
}

function syncFromJson() {
  try {
    const parsed = JSON.parse(jsonContent.value)
    if (parsed && Array.isArray(parsed.steps)) {
      steps.value = parsed.steps
      jsonError.value = ''
      message.success('JSON已同步')
    } else {
      jsonError.value = 'JSON格式错误: 必须包含 steps 数组'
      message.error(jsonError.value)
    }
  } catch (e: any) {
    jsonError.value = `JSON解析错误: ${e.message}`
    message.error(jsonError.value)
  }
}

function getParamSchemas(stepType: StepType) {
  const categories = getStepCategories(props.scriptType)
  for (const category of categories) {
    const step = category.steps.find(s => s.type === stepType)
    if (step) {
      return step.paramSchema || []
    }
  }
  return []
}

function showVariableSelectorFor(field: string) {
  currentInsertField.value = field
  variableSelectorVisible.value = true
  loadVariables()
}

function insertVariable(variable: Variable) {
  if (!selectedStep.value) return

  const placeholder = `\${${variable.name}}`
  // Logic to insert variable into the selected field
  // This depends on the field structure

  variableSelectorVisible.value = false
}

function formatVariablePreview(variable: Variable): string {
  if (variable.is_sensitive) return '***'
  const value = String(variable.value)
  return value.length > 20 ? value.substring(0, 20) + '...' : value
}

function loadVariables() {
  // Load variables from API
  // This would integrate with the variable API
}

function getTypeLabel(type: ScriptType): string {
  const labels: Record<ScriptType, string> = {
    web: 'Web自动化',
    mobile: '移动端',
    api: 'API测试'
  }
  return labels[type]
}

function getFrameworkLabel(framework: Framework): string {
  const labels: Record<Framework, string> = {
    selenium: 'Selenium',
    playwright: 'Playwright',
    appium: 'Appium',
    httprunner: 'HttpRunner'
  }
  return labels[framework]
}

function getTypeIcon(type: ScriptType) {
  // Return appropriate icon component
  return null
}

function showHelp() {
  Modal.info({
    title: '使用帮助',
    content: '从左侧步骤库中拖拽步骤到中间画布，点击步骤编辑属性，支持撤销/重做操作。'
  })
}

// Keyboard shortcuts
function handleKeydown(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
    event.preventDefault()
    undo()
  } else if ((event.ctrlKey || event.metaKey) && (event.key === 'y' || (event.key === 'z' && event.shiftKey))) {
    event.preventDefault()
    redo()
  } else if (event.key === 'Delete' && selectedStepId.value) {
    const step = steps.value.find(s => s.id === selectedStepId.value)
    if (step) removeStep(step)
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  if (steps.value.length > 0) {
    historyStack.value.push(JSON.parse(JSON.stringify(steps.value)))
    historyIndex.value = 0
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.script-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Header */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-light);
  gap: var(--spacing-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.type-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.type-icon {
  font-size: 18px;
  color: var(--color-primary);
}

.framework-badge {
  padding: 2px 8px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  border-radius: var(--radius-sm);
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.mode-switch {
  display: flex;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 2px;
}

.mode-btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.mode-btn.active {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.step-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-right: var(--spacing-sm);
}

/* Body - Three Column Layout */
.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Left: Step Palette */
.step-palette {
  width: 240px;
  background: var(--color-bg-primary);
  border-right: 1px solid var(--color-border-light);
  overflow-y: auto;
  padding: var(--spacing-md);
}

.step-category {
  margin-bottom: var(--spacing-lg);
}

.category-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--spacing-sm);
}

.category-icon {
  font-size: 14px;
}

.category-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

/* Center: Canvas */
.canvas-area {
  flex: 1;
  background: var(--color-bg-secondary);
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.canvas-content {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* JSON Editor */
.json-editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.json-editor {
  flex: 1;
  width: 100%;
  padding: var(--spacing-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  resize: none;
}

.json-editor:focus {
  outline: none;
  border-color: var(--color-primary);
}

.json-error {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-error-bg);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-sm);
}

/* Right: Property Panel */
.property-panel {
  width: 320px;
  background: var(--color-bg-primary);
  border-left: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.panel-header h4 {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

/* Variable Selector */
.variable-selector {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
  overflow: hidden;
  border: 1px solid var(--color-border-light);
}

.variable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-hover);
  border-bottom: 1px solid var(--color-border-light);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.variable-list {
  max-height: 200px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.variable-group {
  margin-bottom: var(--spacing-sm);
}

.variable-group:last-child {
  margin-bottom: 0;
}

.variable-group-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-bg-primary);
  border-radius: var(--radius-xs);
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.variable-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--font-size-xs);
}

.variable-item:hover {
  border-color: var(--color-primary);
  background: var(--color-hover);
}

.var-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
}

.var-type {
  padding: 1px 4px;
  background: var(--color-hover);
  border-radius: var(--radius-xs);
  font-size: 10px;
  color: var(--color-text-secondary);
}

.var-preview {
  color: var(--color-text-tertiary);
  margin-left: auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Scrollbar styling */
.step-palette::-webkit-scrollbar,
.canvas-area::-webkit-scrollbar,
.property-panel::-webkit-scrollbar,
.variable-list::-webkit-scrollbar {
  width: 6px;
}

.step-palette::-webkit-scrollbar-track,
.canvas-area::-webkit-scrollbar-track,
.property-panel::-webkit-scrollbar-track,
.variable-list::-webkit-scrollbar-track {
  background: transparent;
}

.step-palette::-webkit-scrollbar-thumb,
.canvas-area::-webkit-scrollbar-thumb,
.property-panel::-webkit-scrollbar-thumb,
.variable-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.step-palette::-webkit-scrollbar-thumb:hover,
.canvas-area::-webkit-scrollbar-thumb:hover,
.property-panel::-webkit-scrollbar-thumb:hover,
.variable-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}
</style>
