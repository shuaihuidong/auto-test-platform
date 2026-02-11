<template>
  <div class="account-role-manage">
    <a-card :bordered="false">
      <!-- 标签页切换 -->
      <a-tabs v-model:activeKey="activeTab" class="manage-tabs">
        <!-- 账号管理 -->
        <a-tab-pane key="accounts" tab="账号管理">
          <div class="account-section">
            <div class="section-header">
              <h3>账号列表</h3>
              <a-space>
                <a-input-search
                  v-model:value="searchText"
                  placeholder="搜索用户名"
                  style="width: 200px"
                  @search="handleSearch"
                />
                <a-button type="primary" @click="showCreateUser">
                  <PlusOutlined /> 新建账号
                </a-button>
              </a-space>
            </div>

            <a-table
              :columns="userColumns"
              :data-source="filteredUsers"
              :loading="userLoading"
              :pagination="{ pageSize: 10 }"
              row-key="id"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'username'">
                  <a-space>
                    <a-avatar :size="32" :style="{ backgroundColor: getAvatarColor(record.username) }">
                      {{ record.username.charAt(0).toUpperCase() }}
                    </a-avatar>
                    <span>{{ record.username }}</span>
                  </a-space>
                </template>
                <template v-else-if="column.key === 'role'">
                  <a-tag :color="getRoleColor(record.role)">{{ record.role_display }}</a-tag>
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-tag :color="record.is_active ? 'success' : 'default'">
                    {{ record.is_active ? '正常' : '禁用' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'created_at'">
                  {{ formatDate(record.created_at) }}
                </template>
                <template v-else-if="column.key === 'actions'">
                  <a-space>
                    <a-button size="small" @click="showEditUser(record)">
                      <EditOutlined /> 编辑
                    </a-button>
                    <a-button size="small" @click="showChangeRole(record)" v-if="canChangeRole">
                      <UserSwitchOutlined /> 角色
                    </a-button>
                    <a-button size="small" @click="showResetPassword(record)" v-if="canResetPassword">
                      <KeyOutlined /> 重置密码
                    </a-button>
                    <a-popconfirm
                      title="确定删除此账号？"
                      @confirm="handleDeleteUser(record.id)"
                      v-if="canDeleteUser"
                    >
                      <a-button size="small" danger>
                        <DeleteOutlined /> 删除
                      </a-button>
                    </a-popconfirm>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>
        </a-tab-pane>

        <!-- 角色管理 -->
        <a-tab-pane key="roles" tab="角色管理">
          <div class="role-section">
            <div class="section-header">
              <h3>角色列表</h3>
            </div>

            <!-- RabbitMQ 用户管理 - 仅超级管理员可见 -->
            <a-card v-if="isSuperAdmin" title="RabbitMQ 用户管理" style="margin-bottom: 24px;" class="rabbitmq-card">
              <template #extra>
                <a-space>
                  <a-button size="small" @click="loadRabbitMQUsers(true)" :loading="rabbitMQUsersLoading">
                    <SyncOutlined /> 刷新
                  </a-button>
                  <a-tag color="purple">超级管理员专属</a-tag>
                </a-space>
              </template>
              <p style="margin-bottom: 16px; color: rgba(255, 255, 255, 0.8);">
                为执行机客户端创建 RabbitMQ 用户账号。执行机通过网络连接到服务器的 RabbitMQ 时使用此账号。
              </p>
              <a-button type="primary" @click="showCreateRabbitMQUser" style="margin-bottom: 16px;">
                <PlusOutlined /> 创建 RabbitMQ 用户
              </a-button>

              <!-- RabbitMQ 用户列表 -->
              <a-table
                :columns="rabbitMQUserColumns"
                :data-source="rabbitMQUsers"
                :loading="rabbitMQUsersLoading"
                :pagination="false"
                size="small"
                :row-key="'name'"
                class="rabbitmq-users-table"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'name'">
                    <a-space>
                      <a-avatar :size="24" style="background: #667eea;">
                        <UserOutlined />
                      </a-avatar>
                      <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">{{ record.name }}</span>
                    </a-space>
                  </template>
                  <template v-else-if="column.key === 'tags'">
                    <a-tag v-if="record.tags" color="blue">{{ record.tags }}</a-tag>
                    <a-tag v-else color="default">无标签</a-tag>
                  </template>
                  <template v-else-if="column.key === 'actions'">
                    <a-space>
                      <a-button size="small" @click="showChangePasswordRabbitMQ(record)">
                        <KeyOutlined /> 改密
                      </a-button>
                      <a-popconfirm
                        title="确定删除此 RabbitMQ 用户吗？删除后执行机将无法使用此账号连接。"
                        @confirm="handleDeleteRabbitMQUser(record.name)"
                      >
                        <a-button size="small" danger>
                          <DeleteOutlined /> 删除
                        </a-button>
                      </a-popconfirm>
                    </a-space>
                  </template>
                </template>
              </a-table>
            </a-card>

            <a-row :gutter="[16, 16]">
              <a-col :xs="24" :sm="12" :lg="6" v-for="role in roles" :key="role.value">
                <a-card class="role-card" :class="`role-${role.value}`" hoverable>
                  <template #title>
                    <a-space>
                      <SafetyOutlined :style="{ fontSize: '20px' }" />
                      <span>{{ role.label }}</span>
                    </a-space>
                  </template>

                  <div class="role-info">
                    <div class="role-level">
                      <a-tag color="blue">等级 {{ role.level }}</a-tag>
                      <a-tag color="green">{{ role.user_count }} 人</a-tag>
                    </div>

                    <a-divider style="margin: 12px 0" />

                    <div class="role-permissions">
                      <div class="permission-title">权限列表：</div>
                      <a-space wrap>
                        <a-tag v-for="perm in role.permissions" :key="perm" color="purple">
                          {{ getPermissionLabel(perm) }}
                        </a-tag>
                      </a-space>
                    </div>

                    <a-button
                      type="link"
                      block
                      @click="showRoleUsers(role)"
                      :style="{ marginTop: '12px' }"
                    >
                      查看成员 ({{ role.user_count }})
                    </a-button>
                  </div>
                </a-card>
              </a-col>
            </a-row>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 新建/编辑用户对话框 -->
    <a-modal
      v-model:open="userModalVisible"
      :title="userModalTitle"
      width="500px"
      @ok="handleUserOk"
      @cancel="userModalVisible = false"
    >
      <a-form :model="userForm" layout="vertical">
        <a-form-item label="用户名" required>
          <a-input
            v-model:value="userForm.username"
            placeholder="请输入用户名"
            :disabled="isEditMode"
          />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="userForm.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="密码" :required="!isEditMode">
          <a-input-password v-model:value="userForm.password" placeholder="请输入密码" />
          <template v-if="isEditMode">
            <div style="color: #999; font-size: 12px; margin-top: 4px">留空则不修改密码</div>
          </template>
        </a-form-item>
        <a-form-item label="角色" required>
          <a-select v-model:value="userForm.role" placeholder="请选择角色">
            <a-select-option value="super_admin">超级管理员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="tester">测试人员</a-select-option>
            <a-select-option value="guest">访客</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 修改角色对话框 -->
    <a-modal
      v-model:open="roleModalVisible"
      title="修改用户角色"
      width="400px"
      @ok="handleRoleOk"
      @cancel="roleModalVisible = false"
    >
      <a-form layout="vertical">
        <a-form-item label="当前用户">
          <a-input :value="currentUser?.username" disabled />
        </a-form-item>
        <a-form-item label="选择角色" required>
          <a-select v-model:value="newRole" placeholder="请选择角色">
            <a-select-option value="super_admin">超级管理员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="tester">测试人员</a-select-option>
            <a-select-option value="guest">访客</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重置密码确认对话框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="重置密码"
      width="400px"
      @ok="handleResetPasswordOk"
      @cancel="resetPasswordModalVisible = false"
    >
      <a-alert
        message="警告"
        :description="`确定要将用户 ${resetPasswordUser?.username} 的密码重置为默认密码吗？`"
        type="warning"
        show-icon
        style="margin-bottom: 16px"
      />
      <p style="color: rgba(0, 0, 0, 0.65);">
        重置后，该用户的密码将变为 <strong style="color: #f5222d;">123456</strong>。
      </p>
      <p style="color: rgba(0, 0, 0, 0.45); font-size: 12px;">
        为了安全起见，请通知用户尽快修改密码。
      </p>
    </a-modal>

    <!-- 角色成员对话框 -->
    <a-modal
      v-model:open="roleUsersModalVisible"
      :title="`${selectedRole?.label} - 成员列表`"
      width="600px"
      :footer="null"
    >
      <a-list :data-source="roleUsers" :loading="roleUsersLoading">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #avatar>
                <a-avatar :style="{ backgroundColor: getAvatarColor(item.username) }">
                  {{ item.username.charAt(0).toUpperCase() }}
                </a-avatar>
              </template>
              <template #title>{{ item.username }}</template>
              <template #description>{{ item.email }}</template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-modal>

    <!-- 创建 RabbitMQ 用户对话框 -->
    <a-modal
      v-model:open="rabbitMQModalVisible"
      title="创建 RabbitMQ 用户"
      width="500px"
      @ok="handleCreateRabbitMQUser"
      @cancel="rabbitMQModalVisible = false"
    >
      <a-form layout="vertical">
        <a-form-item label="用户名" required>
          <a-input
            v-model:value="rabbitMQForm.username"
            placeholder="请输入 RabbitMQ 用户名"
            :prefix="h(UserOutlined)"
          />
          <template #extra>
            <span style="color: #999; font-size: 12px;">
              建议使用有意义的名称，如：executor-01
            </span>
          </template>
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password
            v-model:value="rabbitMQForm.password"
            placeholder="请输入密码"
          />
          <template #extra>
            <span style="color: #999; font-size: 12px;">
              密码将提供给执行机用户，用于配置执行机客户端
            </span>
          </template>
        </a-form-item>
        <a-form-item label="标签">
          <a-select
            v-model:value="rabbitMQForm.tags"
            placeholder="选择用户标签"
            mode="tags"
          >
            <a-select-option value="management">management</a-select-option>
            <a-select-option value="policymaker">policymaker</a-select-option>
            <a-select-option value="monitoring">monitoring</a-select-option>
          </a-select>
          <template #extra>
            <span style="color: #999; font-size: 12px;">
              management: 可访问管理插件；policymaker: 可制定策略；monitoring: 可访问监控插件
            </span>
          </template>
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="rabbitMQModalVisible = false">取消</a-button>
        <a-button type="primary" @click="handleCreateRabbitMQUser" :loading="rabbitMQCreating">
          创建用户
        </a-button>
      </template>
    </a-modal>

    <!-- RabbitMQ 用户创建成功对话框 -->
    <a-modal
      v-model:open="rabbitMQSuccessVisible"
      title="用户创建成功"
      width="500px"
      :footer="null"
    >
      <a-result
        status="success"
        title="RabbitMQ 用户创建成功"
        sub-title="请将以下信息提供给执行机用户"
      >
        <template #extra>
          <a-descriptions bordered :column="1" style="margin-top: 16px;">
            <a-descriptions-item label="用户名">{{ rabbitMQCreatedUser.username }}</a-descriptions-item>
            <a-descriptions-item label="密码">
              <a-typography-text copyable>{{ rabbitMQCreatedUser.password }}</a-typography-text>
            </a-descriptions-item>
            <a-descriptions-item label="标签">{{ rabbitMQCreatedUser.tags }}</a-descriptions-item>
          </a-descriptions>
          <a-alert
            type="info"
            message="配置说明"
            description="在执行机客户端配置向导的「RabbitMQ 配置」页面中，填写上述用户名和密码。如果执行机和服务器在不同电脑，主机地址需填写服务器的实际 IP 地址。"
            show-icon
            style="margin-top: 16px;"
          />
          <a-button type="primary" @click="rabbitMQSuccessVisible = false" style="margin-top: 16px;">
            知道了
          </a-button>
        </template>
      </a-result>
    </a-modal>

    <!-- 修改 RabbitMQ 用户密码对话框 -->
    <a-modal
      v-model:open="rabbitMQPasswordModalVisible"
      title="修改 RabbitMQ 用户密码"
      width="450px"
      @ok="handleChangeRabbitMQPassword"
      @cancel="rabbitMQPasswordModalVisible = false"
    >
      <a-form layout="vertical">
        <a-form-item label="用户名">
          <a-input
            :value="rabbitMQPasswordUser.username"
            disabled
            :prefix="h(UserOutlined)"
          />
        </a-form-item>
        <a-form-item label="新密码" required>
          <a-input-password
            v-model:value="rabbitMQPasswordForm.password"
            placeholder="请输入新密码"
          />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="rabbitMQPasswordModalVisible = false">取消</a-button>
        <a-button type="primary" @click="handleChangeRabbitMQPassword" :loading="rabbitMQPasswordUpdating">
          确认修改
        </a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserSwitchOutlined,
  SafetyOutlined,
  KeyOutlined,
  UserOutlined,
  SyncOutlined
} from '@ant-design/icons-vue'
import { userApi } from '@/api/user'
import { roleApi } from '@/api/role'
import type { Role } from '@/api/role'
import { useUserStore } from '@/store/user'
import axios from 'axios'

const userStore = useUserStore()

const activeTab = ref('accounts')
const searchText = ref('')
const userLoading = ref(false)
const users = ref<any[]>([])
const roles = ref<Role[]>([])

const userModalVisible = ref(false)
const userModalTitle = ref('新建账号')
const isEditMode = ref(false)
const userForm = ref({
  id: 0,
  username: '',
  email: '',
  password: '',
  role: 'guest'
})

const roleModalVisible = ref(false)
const currentUser = ref<any>(null)
const newRole = ref('')

// RabbitMQ 用户管理相关
const rabbitMQModalVisible = ref(false)
const rabbitMQSuccessVisible = ref(false)
const rabbitMQCreating = ref(false)
const rabbitMQForm = ref({
  username: '',
  password: '',
  tags: 'management'
})
const rabbitMQCreatedUser = ref({
  username: '',
  password: '',
  tags: ''
})

const roleUsersModalVisible = ref(false)
const selectedRole = ref<Role | null>(null)
const roleUsers = ref<any[]>([])
const roleUsersLoading = ref(false)

// 重置密码相关
const resetPasswordUser = ref<any>(null)
const resetPasswordModalVisible = ref(false)

// RabbitMQ 用户列表管理
const rabbitMQUsers = ref<any[]>([])
const rabbitMQUsersLoading = ref(false)
const rabbitMQPasswordModalVisible = ref(false)
const rabbitMQPasswordForm = ref({
  password: ''
})
const rabbitMQPasswordUser = ref<any>(null)
const rabbitMQPasswordUpdating = ref(false)

const rabbitMQUserColumns = [
  { title: '用户名', key: 'name', width: 200 },
  { title: '标签', key: 'tags', width: 150 },
  { title: '操作', key: 'actions', width: 200 }
]

const userColumns = [
  { title: '用户名', key: 'username', width: 200 },
  { title: '邮箱', key: 'email', dataIndex: 'email' },
  { title: '角色', key: 'role', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 300, fixed: 'right' }
]

const filteredUsers = computed(() => {
  if (!searchText.value) return users.value
  return users.value.filter(u =>
    u.username.toLowerCase().includes(searchText.value.toLowerCase()) ||
    u.email.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const canChangeRole = computed(() => {
  return userStore.user?.role === 'super_admin'
})

const canDeleteUser = computed(() => {
  return userStore.user?.role === 'admin' || userStore.user?.role === 'super_admin'
})

const canResetPassword = computed(() => {
  return userStore.user?.role === 'admin' || userStore.user?.role === 'super_admin'
})

const isSuperAdmin = computed(() => {
  return userStore.user?.role === 'super_admin'
})

async function loadUsers() {
  userLoading.value = true
  try {
    const res = await userApi.getList()
    users.value = res.results || []
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    userLoading.value = false
  }
}

async function loadRoles() {
  try {
    const res = await roleApi.getList()
    roles.value = res.results || []
  } catch (error) {
    // 错误已由拦截器处理
  }
}

function handleSearch() {
  // 搜索逻辑由 computed 处理
}

function showCreateUser() {
  isEditMode.value = false
  userModalTitle.value = '新建账号'
  userForm.value = {
    id: 0,
    username: '',
    email: '',
    password: '',
    role: 'guest'
  }
  userModalVisible.value = true
}

function showEditUser(user: any) {
  isEditMode.value = true
  userModalTitle.value = '编辑账号'
  userForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    password: '',
    role: user.role
  }
  userModalVisible.value = true
}

async function handleUserOk() {
  if (!userForm.value.username || !userForm.value.email) {
    message.error('请填写完整信息')
    return
  }
  if (!isEditMode.value && !userForm.value.password) {
    message.error('请输入密码')
    return
  }

  try {
    if (isEditMode.value) {
      const updateData: any = {
        email: userForm.value.email,
        role: userForm.value.role
      }
      // 只有输入了密码才发送
      if (userForm.value.password) {
        updateData.password = userForm.value.password
      }
      await userApi.update(userForm.value.id, updateData)
      message.success('更新成功')
    } else {
      await userApi.create({
        username: userForm.value.username,
        email: userForm.value.email,
        password: userForm.value.password,
        password_confirm: userForm.value.password,
        role: userForm.value.role
      })
      message.success('创建成功')
    }
    userModalVisible.value = false
    loadUsers()
    loadRoles()
  } catch (error: any) {
    // 显示详细的验证错误
    if (error.response?.data) {
      const errors = error.response.data
      if (typeof errors === 'object' && !Array.isArray(errors)) {
        // 字段级别的验证错误
        const errorMessages: string[] = []
        for (const [field, messages] of Object.entries(errors)) {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`)
          } else if (typeof messages === 'string') {
            errorMessages.push(messages)
          }
        }
        if (errorMessages.length > 0) {
          message.error(errorMessages.join('\n'))
        } else {
          message.error('创建失败，请检查输入')
        }
      } else if (typeof errors === 'string') {
        message.error(errors)
      } else {
        message.error('创建失败，请检查输入')
      }
    } else {
      message.error('创建失败，请检查网络连接')
    }
  }
}

async function handleDeleteUser(id: number) {
  try {
    await userApi.delete(id)
    message.success('删除成功')
    loadUsers()
    loadRoles()
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('删除失败，请检查网络连接')
    }
  }
}

function showChangeRole(user: any) {
  currentUser.value = user
  newRole.value = user.role
  roleModalVisible.value = true
}

function showResetPassword(user: any) {
  resetPasswordUser.value = user
  resetPasswordModalVisible.value = true
}

async function handleResetPasswordOk() {
  if (!resetPasswordUser.value) return

  try {
    const res = await userApi.resetPassword(resetPasswordUser.value.id)
    message.success({
      content: `${res.message}`,
      duration: 5
    })
    // 显示新密码
    Modal.info({
      title: '密码重置成功',
      content: `用户 ${resetPasswordUser.value.username} 的新密码为：${res.default_password}，请通知用户及时修改密码。`,
      okText: '知道了'
    })
    resetPasswordModalVisible.value = false
    resetPasswordUser.value = null
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('重置密码失败')
    }
  }
}

async function handleRoleOk() {
  if (!newRole.value) {
    message.error('请选择角色')
    return
  }

  try {
    await userApi.setRole(currentUser.value.id, newRole.value)
    message.success('角色修改成功')
    roleModalVisible.value = false
    loadUsers()
    loadRoles()
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else if (error.response?.data) {
      message.error('角色修改失败')
    } else {
      message.error('操作失败，请检查网络连接')
    }
  }
}

async function showRoleUsers(role: Role) {
  selectedRole.value = role
  roleUsersModalVisible.value = true
  roleUsersLoading.value = true

  try {
    const res = await roleApi.getUsers(role.value)
    roleUsers.value = res.users || []
  } catch (error) {
    roleUsers.value = []
  } finally {
    roleUsersLoading.value = false
  }
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    super_admin: 'red',
    admin: 'orange',
    tester: 'blue',
    guest: 'default'
  }
  return colors[role] || 'default'
}

function getAvatarColor(username: string): string {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae', '#1890ff']
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

function getPermissionLabel(perm: string): string {
  const labels: Record<string, string> = {
    view: '查看',
    list: '列表',
    create: '创建',
    update: '更新',
    delete: '删除',
    execute: '执行',
    manage_users: '用户管理',
    manage_settings: '系统设置'
  }
  return labels[perm] || perm
}

function formatDate(date: string): string {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// RabbitMQ 用户管理函数
function showCreateRabbitMQUser() {
  rabbitMQForm.value = {
    username: '',
    password: '',
    tags: 'management'
  }
  rabbitMQModalVisible.value = true
}

async function handleCreateRabbitMQUser() {
  if (!rabbitMQForm.value.username || !rabbitMQForm.value.password) {
    message.error('请填写用户名和密码')
    return
  }

  rabbitMQCreating.value = true
  try {
    const response = await axios.post('/api/users/create_rabbitmq_user/', {
      username: rabbitMQForm.value.username,
      password: rabbitMQForm.value.password,
      tags: rabbitMQForm.value.tags
    })

    // 保存创建的用户信息
    rabbitMQCreatedUser.value = {
      username: rabbitMQForm.value.username,
      password: rabbitMQForm.value.password,
      tags: rabbitMQForm.value.tags
    }

    // 关闭创建对话框
    rabbitMQModalVisible.value = false

    // 显示成功对话框
    rabbitMQSuccessVisible.value = true

    message.success('RabbitMQ 用户创建成功')
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('创建用户失败，请检查网络连接和 RabbitMQ 服务状态')
    }
  } finally {
    rabbitMQCreating.value = false
  }
}

// 加载 RabbitMQ 用户列表
async function loadRabbitMQUsers(showSuccess = false) {
  if (!isSuperAdmin.value) return

  rabbitMQUsersLoading.value = true
  try {
    const response = await axios.get('/api/users/list_rabbitmq_users/')
    rabbitMQUsers.value = response.data.users || []
    if (showSuccess) {
      message.success('RabbitMQ 用户列表已刷新')
    }
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('获取用户列表失败，请检查 RabbitMQ 服务状态')
    }
    rabbitMQUsers.value = []
  } finally {
    rabbitMQUsersLoading.value = false
  }
}

// 删除 RabbitMQ 用户
async function handleDeleteRabbitMQUser(username: string) {
  try {
    await axios.post('/api/users/delete_rabbitmq_user/', { username })
    message.success(`RabbitMQ 用户 ${username} 已删除`)
    // 刷新用户列表
    loadRabbitMQUsers()
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('删除用户失败，请检查网络连接')
    }
  }
}

// 显示修改密码对话框
function showChangePasswordRabbitMQ(user: any) {
  rabbitMQPasswordUser.value = {
    username: user.name
  }
  rabbitMQPasswordForm.value = {
    password: ''
  }
  rabbitMQPasswordModalVisible.value = true
}

// 修改 RabbitMQ 用户密码
async function handleChangeRabbitMQPassword() {
  if (!rabbitMQPasswordForm.value.password) {
    message.error('请输入新密码')
    return
  }

  rabbitMQPasswordUpdating.value = true
  try {
    await axios.post('/api/users/update_rabbitmq_user_password/', {
      username: rabbitMQPasswordUser.value.username,
      password: rabbitMQPasswordForm.value.password
    })
    message.success('密码修改成功')
    rabbitMQPasswordModalVisible.value = false
    rabbitMQPasswordForm.value = { password: '' }
    rabbitMQPasswordUser.value = null
  } catch (error: any) {
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('修改密码失败，请检查网络连接')
    }
  } finally {
    rabbitMQPasswordUpdating.value = false
  }
}

onMounted(() => {
  loadUsers()
  loadRoles()
  // 如果是超级管理员，加载 RabbitMQ 用户列表
  if (isSuperAdmin.value) {
    loadRabbitMQUsers()
  }
})
</script>

<style scoped>
.account-role-manage {
  padding: 0;
}

.manage-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

/* 角色卡片样式 */
.role-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.role-card :deep(.ant-card-head-title) {
  font-weight: 600;
}

.role-card.role-super_admin {
  border-top: 3px solid #ff4d4f;
}

.role-card.role-admin {
  border-top: 3px solid #fa8c16;
}

.role-card.role-tester {
  border-top: 3px solid #1890ff;
}

.role-card.role-guest {
  border-top: 3px solid #d9d9d9;
}

.role-info {
  padding: 0;
}

.role-level {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-permissions {
  margin-top: 8px;
}

.permission-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

/* RabbitMQ 卡片样式 */
.rabbitmq-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.rabbitmq-card :deep(.ant-card-head-title) {
  color: white;
}

.rabbitmq-card :deep(.ant-card-body) {
  color: rgba(255, 255, 255, 0.9);
}

.rabbitmq-card p {
  color: rgba(255, 255, 255, 0.85) !important;
}

/* RabbitMQ 用户表格样式 */
.rabbitmq-users-table {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.rabbitmq-users-table :deep(.ant-table) {
  background: transparent;
}

.rabbitmq-users-table :deep(.ant-table-thead > tr > th) {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.rabbitmq-users-table :deep(.ant-table-tbody > tr > td) {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.rabbitmq-users-table :deep(.ant-table-tbody > tr:hover > td) {
  background: rgba(255, 255, 255, 0.1);
}

.rabbitmq-users-table :deep(.ant-empty-description) {
  color: rgba(255, 255, 255, 0.7);
}

/* 响应式 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
