<template>
  <div class="project-list">
    <div class="page-header">
      <h2>项目管理</h2>
      <a-space>
        <a-button type="primary" @click="showCreateModal">
          <template #icon><PlusOutlined /></template>
          新建项目
        </a-button>
      </a-space>
    </div>

    <a-spin :spinning="loading">
      <div v-if="projects.length > 0" class="project-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card"
        >
          <div class="card-header">
            <a-tag :color="getTypeColor(project.type)">{{ getTypeLabel(project.type) }}</a-tag>
            <a-dropdown>
              <a class="action-icon"><MoreOutlined /></a>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="showEditModal(project)">
                    <EditOutlined /> 编辑
                  </a-menu-item>
                  <a-menu-item @click="handleDelete(project)">
                    <DeleteOutlined /> 删除
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
          <div class="card-body">
            <h3 class="project-name">{{ project.name }}</h3>
            <p class="project-desc">{{ project.description || '暂无描述' }}</p>
            <div class="project-meta">
              <span><FileTextOutlined /> {{ project.script_count }} 个脚本</span>
              <span><CalendarOutlined /> {{ formatDate(project.created_at) }}</span>
            </div>
          </div>
          <div class="card-footer">
            <a-button block @click="goToScripts(project.id)">
              进入项目 <ArrowRightOutlined />
            </a-button>
          </div>
        </div>
      </div>

      <a-empty v-else description="暂无项目" />
    </a-spin>

    <!-- 新建/编辑项目弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="项目名称" required>
          <a-input v-model:value="form.name" placeholder="请输入项目名称" />
        </a-form-item>
        <a-form-item label="项目类型" required>
          <a-select v-model:value="form.type" placeholder="请选择项目类型">
            <a-select-option value="web">Web自动化</a-select-option>
            <a-select-option value="mobile">移动端自动化</a-select-option>
            <a-select-option value="api">API接口测试</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="项目描述">
          <a-textarea v-model:value="form.description" :rows="4" placeholder="请输入项目描述" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  FileTextOutlined,
  CalendarOutlined,
  ArrowRightOutlined
} from '@ant-design/icons-vue'
import { getProjectList, createProject, updateProject, deleteProject } from '@/api/project'
import type { Project, ProjectForm } from '@/types/project'

const router = useRouter()
const loading = ref(false)
const projects = ref<Project[]>([])
const modalVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const form = ref<ProjectForm>({
  name: '',
  description: '',
  type: 'web'
})

async function loadProjects() {
  loading.value = true
  try {
    const res = await getProjectList()
    projects.value = res.results
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

function showCreateModal() {
  isEdit.value = false
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    type: 'web'
  }
  modalVisible.value = true
}

function showEditModal(project: Project) {
  isEdit.value = true
  editingId.value = project.id
  form.value = {
    name: project.name,
    description: project.description,
    type: project.type
  }
  modalVisible.value = true
}

async function handleModalOk() {
  if (!form.value.name) {
    message.error('请输入项目名称')
    return
  }

  try {
    if (isEdit.value && editingId.value) {
      await updateProject(editingId.value, form.value)
      message.success('项目更新成功')
    } else {
      await createProject(form.value)
      message.success('项目创建成功')
    }
    modalVisible.value = false
    loadProjects()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function handleModalCancel() {
  modalVisible.value = false
}

function handleDelete(project: Project) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除项目 "${project.name}" 吗？`,
    onOk: async () => {
      try {
        await deleteProject(project.id)
        message.success('删除成功')
        loadProjects()
      } catch (error) {
        // 错误已由拦截器处理
      }
    }
  })
}

function goToScripts(projectId: number) {
  router.push(`/projects/${projectId}`)
}

function getTypeLabel(type: string) {
  const labels: Record<string, string> = {
    web: 'Web自动化',
    mobile: '移动端',
    api: 'API测试'
  }
  return labels[type] || type
}

function getTypeColor(type: string) {
  const colors: Record<string, string> = {
    web: 'blue',
    mobile: 'green',
    api: 'orange'
  }
  return colors[type] || 'default'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD')
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-list {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl, 24px);
}

.page-header h2 {
  margin: 0;
  font-size: var(--font-size-3xl, 28px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #E5E7EB);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg, 24px);
}

.project-card {
  background: var(--color-bg-elevated, #1E2A5C);
  border: 1px solid var(--color-border, #1E2A5C);
  border-radius: var(--radius-lg, 8px);
  transition: all var(--transition-base, 0.2s);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.project-card:hover {
  border-color: var(--color-primary, #E5E7EB);
  box-shadow: 0 2px 8px rgba(229, 231, 235, 0.3);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md, 16px) var(--spacing-lg, 20px);
  border-bottom: 1px solid var(--color-border-light, #1A2452);
}

.action-icon {
  color: var(--color-text-tertiary, #6B7280);
  transition: color var(--transition-fast, 0.15s);
}

.action-icon:hover {
  color: var(--color-text-primary, #E5E7EB);
}

.card-body {
  padding: var(--spacing-lg, 20px);
  flex: 1;
}

.project-name {
  margin: 0 0 var(--spacing-sm, 8px) 0;
  font-size: var(--font-size-lg, 18px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #E5E7EB);
}

.project-desc {
  margin: 0 0 var(--spacing-lg, 16px) 0;
  color: var(--color-text-secondary, #9CA3AF);
  font-size: var(--font-size-base, 14px);
  min-height: 40px;
  line-height: 1.5;
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm, 8px);
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-tertiary, #6B7280);
}

.project-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-footer {
  padding: var(--spacing-md, 16px) var(--spacing-lg, 20px);
  border-top: 1px solid var(--color-border-light, #1A2452);
}

/* Tag colors override */
:deep(.ant-tag) {
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  color: #1F2937;
}

/* Button styles */
/* Note: Buttons inherit styles from App.vue for consistent hover transitions */

/* Empty state */
:deep(.ant-empty-description) {
  color: var(--color-text-tertiary, #6B7280);
}
</style>
