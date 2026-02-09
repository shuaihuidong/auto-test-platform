<template>
  <div class="user-manage">
    <div class="page-header">
      <h2>用户管理</h2>
      <a-button type="primary" @click="showCreateModal">
        <PlusOutlined /> 新建用户
      </a-button>
    </div>

    <a-card>
      <a-table
        :columns="columns"
        :data-source="users"
        :loading="loading"
        :pagination="{ pageSize: 20 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
              {{ record.role === 'admin' ? '管理员' : '普通用户' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'is_active'">
            <a-badge :status="record.is_active ? 'success' : 'default'" :text="record.is_active ? '启用' : '禁用'" />
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="editUser(record)">
                <EditOutlined /> 编辑
              </a-button>
              <a-popconfirm
                v-if="record.id !== currentUserId"
                title="确定删除此用户？"
                @confirm="handleDelete(record)"
              >
                <a-button size="small" danger>
                  <DeleteOutlined />
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 新建/编辑用户弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑用户' : '新建用户'"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="用户名" required>
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="form.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="密码" :required="!isEdit">
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="角色" required>
          <a-select v-model:value="form.role">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.user?.id)

const loading = ref(false)
const users = ref<any[]>([])
const modalVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  role: 'user'
})

const columns = [
  { title: 'ID', key: 'id', dataIndex: 'id', width: 80 },
  { title: '用户名', key: 'username', dataIndex: 'username' },
  { title: '邮箱', key: 'email', dataIndex: 'email' },
  { title: '角色', key: 'role', dataIndex: 'role', width: 120 },
  { title: '状态', key: 'is_active', dataIndex: 'is_active', width: 100 },
  { title: '创建时间', key: 'created_at', dataIndex: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 160 }
]

async function loadUsers() {
  loading.value = true
  try {
    const res = await getUserList()
    users.value = res.results
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
    username: '',
    email: '',
    password: '',
    role: 'user'
  }
  modalVisible.value = true
}

function editUser(user: any) {
  isEdit.value = true
  editingId.value = user.id
  form.value = {
    username: user.username,
    email: user.email,
    password: '',
    role: user.role
  }
  modalVisible.value = true
}

async function handleModalOk() {
  if (!form.value.username || !form.value.email) {
    message.error('请填写完整信息')
    return
  }

  if (!isEdit.value && !form.value.password) {
    message.error('请输入密码')
    return
  }

  try {
    if (isEdit.value && editingId.value) {
      await updateUser(editingId.value, form.value)
      message.success('更新成功')
    } else {
      await createUser(form.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadUsers()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function handleModalCancel() {
  modalVisible.value = false
}

async function handleDelete(user: any) {
  try {
    await deleteUser(user.id)
    message.success('删除成功')
    loadUsers()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-manage {
  max-width: 1200px;
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
</style>
